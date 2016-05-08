from libs.module import *
from libs.uds import *
from libs.frag import *
import json
import re
import collections
import ast
import time


class mod_stat(CANModule):
    name = "Service discovery and statistic"

    help = """
    
    This module doing statistic for found CAN messages, putting into STDOUT or file (text/csv).
    Good to see anomalies, behaviour and discovery new IDs
    
    Init parameters: NONE
       
    """

    _bodyList = None
    _logFile = False
    ISOList = None
    UDSList = None
    id = 3
    _active = True
    version = 1.0

    def get_status(self, def_in = 0):
        return "Current status: " + str(self._active) + "\nSniffed frames (overall): " + str(self.get_num(-1))+"\nCurrent BUFF: index - " + str(self._index) + " name - " + self.all_frames[self._index]['name'] + \
               "\nAll buffers: \n\t" + \
            '\n\t'.join([buf['name'] + "\n\t\tindex: " + str(cnt) + ' sniffed: ' + str(len(buf['buf'])) for buf,cnt in zip(self.all_frames,range(0,len(self.all_frames)))])

    def do_init(self, params):
        self.all_frames = [{'name':'start_buffer','buf':[]}]
        self._index = 0
        self.meta_data = {}
        self._bodyList = collections.OrderedDict()
        self.shift = params.get('uds_shift', 8)

        if 'meta_file' in params:
            self.dprint(1, self.do_load_meta(params['meta_file']))

        self._cmdList['p'] = ["Print current table", 0, "", self.do_print, True]

        self._cmdList['a'] = ["Analyses of captured traffic", 1, "<UDS|ISO|FRAG|ALL(defaut)>,[buffer index]", self.do_anal, True]
        self._cmdList['u'] = ["    - UDS shift value",1,"[shift value]", self.change_shift, True]

        self._cmdList['D'] = ["Switch sniffing to a new buffer", 1, "[name]", self.new_diff, True]
        self._cmdList['I'] = ["Print Diff between two buffers", 1, "[buffer index 1], [buffer index 2], [uniq values max]", self.print_diff, True]
        self._cmdList['N'] = ["Print Diff between two buffers (new ID only)", 1, "[buffer index 1], [buffer index 2]", self.print_diff_id, True]

        self._cmdList['Y'] = ["Dump Diff in replay format", 1, "<filename>,[buffer index ,buffer index], [uniq values max]", self.print_dump_diff, True]
        self._cmdList['y'] = ["Dump Diff in replay format (new ID)", 1, "<filename>,[buffer index 1] , [buffer index 2]", self.print_dump_diff_id, True]
        self._cmdList['F'] = ["Search ID in all buffers", 1, "<ID>", self.search_id, True]
        self._cmdList['c'] = ["Clean table, remove buffers", 0, "", self.do_clean, True]

        self._cmdList['i'] = ["Meta-data: add description for frames", 1, "<ID>, <data regex ASCII HEX>, <description>", self.do_add_meta_descr_data, True]
        self._cmdList['l'] = ["Load meta-data", 1, "<filename>", self.do_load_meta, True]
        self._cmdList['z'] = ["Save meta-data", 1, "<filename>", self.do_save_meta, True]
        self._cmdList['r'] = ["Dump all buffers in replay format", 1, " <filename>, [index]", self.do_dump_replay, True]
        self._cmdList['d'] = ["Dump STAT (all buffers) in CSV format", 1, " <filename>, [index]", self.do_dump_csv, True]
        self._cmdList['g'] = ["Get DELAY value for gen_ping/gen_fuzz (EXPERIMENTAL)",1,"<Bus SPEED in Kb/s>", self.get_delay, True]

    def get_delay(self, def_in, speed):
        _speed = float(speed)*1024
        curr_1 = len(self.all_frames[self._index]['buf'])
        time.sleep(3)
        curr_2 = len(self.all_frames[self._index]['buf'])
        diff = curr_2 - curr_1
        speed = int((diff * 80)/3)
        delay = 1/int((_speed - speed)/80)
        return "Avrg. delay: " + str(delay)

    def change_shift(self, def_in, val):
        if val.strip()[0:2] == '0x':
            value = int(val,16)
        else:
            value = int(val)
        self.shift = value
        return "UDS shift: " + hex(self.shift)

    def do_add_meta_descr_data(self, def_in, input_params):
        try:
            fid, body, descr = input_params.split(',')
            if fid.strip().find('0x') == 0:
                num_fid = int(fid, 16)
            else:
                num_fid = int(fid)
            if 'description' not in self.meta_data:
                self.meta_data['description'] = {}

            self.meta_data['description'][(num_fid, body.strip().upper())] = descr.strip()

            return "Description data has been added"
        except Exception as e:
            return "Description data META error: " + str(e)

    def get_meta_descr(self, fid, msg):
        descrs = self.meta_data.get('description', {})
        for (key, body) in list(descrs.keys()):
            if fid == key:
                if(re.match(body, self.get_hex(msg), re.IGNORECASE)):
                    return str(descrs[(key, body)])
        return "  "


    def do_load_meta(self, def_in, filename):
        try:
            data = ""
            with open(filename.strip(), "r") as ins:
                for line in ins:
                    data += line
            self.meta_data = ast.literal_eval(data)

        except Exception as e:
            return "Can't load META: " + str(e)
        return "Loaded META from " + filename

    def do_save_meta(self, def_in, filename):
        try:
            _file = open(filename.strip(), 'w')
            _file.write(str(self.meta_data))
            _file.close()
        except Exception as e:
            return "Can't save META: " + str(e)
        return "Saved META to " + filename

    # Detect ASCII data
    @staticmethod
    def ret_ascii(text_array):
        return_str = ""
        for byte in text_array:
            if 31 < byte < 127:
                return_str += chr(byte)
            else:
                return_str += '.'
        return return_str

    # Detect ASCII data
    @staticmethod
    def is_ascii(text_array):
        bool_ascii = False
        ascii_cnt = 0
        pre_byte = False

        for byte in text_array:
            if 31 < byte < 127:
                if pre_byte:
                    ascii_cnt += 1
                    if ascii_cnt > 1:
                        bool_ascii = True
                        break
                else:
                    pre_byte = True
            else:
                pre_byte = False
                ascii_cnt = 0

        if ascii_cnt > 5:
            bool_ascii = True

        return bool_ascii

    def get_num(self,_index = -1):
        count = 0
        if _index == -1:
            for buf in self.all_frames:
                count += len(buf['buf'])
        else:
            count = len(self.all_frames[_index]['buf'])

        return count

    @staticmethod
    def create_short_table(input_frames):
        _bodyList = collections.OrderedDict()
        for can_msg in input_frames:
            if can_msg.CANFrame.frame_id not in _bodyList:
                _bodyList[can_msg.CANFrame.frame_id] = collections.OrderedDict()
                _bodyList[can_msg.CANFrame.frame_id][(
                can_msg.CANFrame.frame_length,
                can_msg.CANFrame.frame_raw_data,
                can_msg.bus,
                can_msg.CANFrame.frame_ext)
                    ] = 1
            else:
                if (can_msg.CANFrame.frame_length,
                    can_msg.CANFrame.frame_raw_data,
                    can_msg.bus,
                    can_msg.CANFrame.frame_ext) not in _bodyList[can_msg.CANFrame.frame_id]:
                    _bodyList[can_msg.CANFrame.frame_id][(
                        can_msg.CANFrame.frame_length,
                        can_msg.CANFrame.frame_raw_data,
                        can_msg.bus,
                        can_msg.CANFrame.frame_ext)
                        ] = 1
                else:
                    _bodyList[can_msg.CANFrame.frame_id][(
                    can_msg.CANFrame.frame_length,
                    can_msg.CANFrame.frame_raw_data,
                    can_msg.bus,
                    can_msg.CANFrame.frame_ext)
                    ] += 1
        return _bodyList

    def find_iso_tp(self, in_list):
        message_iso = {}
        iso_list = []
        for can_msg in in_list:
            if can_msg.CANFrame.frame_id not in message_iso:
                message_iso[can_msg.CANFrame.frame_id] = ISOTPMessage(can_msg.CANFrame.frame_id)

            if 1 < can_msg.CANFrame.frame_length:
                ret = message_iso[can_msg.CANFrame.frame_id].add_can(can_msg.CANFrame)
                if ret < 0:
                    del message_iso[can_msg.CANFrame.frame_id]
                elif ret == 1:
                    iso_list.append(message_iso[can_msg.CANFrame.frame_id])
                    del message_iso[can_msg.CANFrame.frame_id]
            else:
                del message_iso[can_msg.CANFrame.frame_id]
        return iso_list

    def find_uds(self, iso_list):
        uds_list = UDSMessage(self.shift)
        for message_iso in iso_list:
            uds_list.handle_message(message_iso)
        return uds_list

    def find_loops(self):
        frg_list = collections.OrderedDict()
        for fid, lst in self._bodyList.items():
            frg_list[fid] = FragmentedCAN()
            for (lenX, msg, bus, mod), cnt in lst.items():
                frg_list[fid].add_can_loop(CANMessage.init_data(fid, lenX, msg))

        return frg_list

    def do_anal(self, def_in, format = "ALL"):

        format.upper()

        params = format.split(",")
        if len(params) == 1:
            _format = params[0].strip()
            _index  = -1
        else:
           _format = params[0].strip()
           _index  = int(params[1])
        temp_buf = []
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']

        self._bodyList = self.create_short_table(temp_buf)
        iso_tp_list = self.find_iso_tp(temp_buf)
        uds_list = self.find_uds(iso_tp_list)
        loops_list = self.find_loops()
        ret_str = ""

        _iso_tbl = collections.OrderedDict()
        for msg in iso_tp_list:
            if msg.message_id not in _iso_tbl:
                _iso_tbl[msg.message_id] = collections.OrderedDict()
                _iso_tbl[msg.message_id][(msg.message_length,  bytes(msg.message_data))] = 1
            else:
                if (msg.message_length, bytes(msg.message_data)) in _iso_tbl[msg.message_id]:
                    _iso_tbl[msg.message_id][(msg.message_length,  bytes(msg.message_data))] += 1
                else:
                    _iso_tbl[msg.message_id][(msg.message_length, bytes(msg.message_data))] = 1

        if _format.strip() not in ["ISO","FRAG"]:
            # Print out UDS
            ret_str += "UDS Detected:\n\n"
            for fid, services in uds_list.sessions.items():
                for service, body in services.items():
                    text = " (N/A) "
                    if service in UDSMessage.services_base:
                        for sub in UDSMessage.services_base[service]:
                            if list(sub.keys())[0] == body['sub'] or None:
                                text = " (" + list(sub.values())[0] + ") "
                        if text == " (N/A) ":
                            text = " (" + list(UDSMessage.services_base[service][0].values())[0] + ") "
                    if body['status'] == 1:
                        data =  body['response']['data']
                        data_ascii = "\n"
                        if self.is_ascii(body['response']['data']):
                            data_ascii = "\n\t\tASCII: " + self.ret_ascii(data)+"\n"
                        ret_str += "\n\tID: " + hex(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                            hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tResponse: " + self.get_hex(bytes(data)) + data_ascii
                    elif body['status'] == 2:
                       ret_str += "\n\tID: " + hex(fid) + " Service: " + str(hex(service)) + " Sub: " + (str(
                            hex(body['sub'])) if body['sub'] else "None") + text + "\n\t\tError: " + body['response']['error']

        if _format.strip() not in ["ISO", "UDS"]:
            # Print detected loops
            ret_str += "\n\nDe-Fragmented frames (using loop-based detection):\n"
            local_temp = {}
            for fid, data in loops_list.items():
                data.clean_build_loop()
                for message in data.messages:
                    if (fid, bytes(message['message_data'])) not in local_temp:
                        ret_str += "\n\tID " + hex(fid) + " and length " + str(message['message_length']) + "\n"
                        ret_str += "\t\tData: " + self.get_hex(bytes(message['message_data']))
                        if self.is_ascii(message['message_data']):
                            ret_str += "\n\t\tASCII: " + self.ret_ascii(bytes(message['message_data'])) + "\n\n"
                        local_temp[(fid, bytes(message['message_data']))] = None

        if _format.strip() not in ["UDS","FRAG"]:
            # Print out ISOTP messages
            ret_str += "\nISO TP Messages:\n\n"
            for fid, lst in _iso_tbl.items():
                ret_str += "\tID: " + hex(fid) + "\n"
                for (lenX, msg), cnt in lst.items():
                    ret_str += "\t\tDATA: " + self.get_hex(msg)
                    if self.is_ascii(msg):
                        ret_str += "\n\t\tASCII: " + self.ret_ascii(msg)
                    ret_str += "\n"

        return ret_str

    def search_id(self, def_in, idf):
        idf = int(idf) if not idf.strip()[0:2] == '0x' else int(idf,16)
        table = "Search for " + hex(idf) + "\n"
        rows = []
        for buf in self.all_frames:
            rows.append(['Dump:', buf['name'], ' ',  ' ', ' ', ' ', ' '])
            rows.append(['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT'])
            short = self.create_short_table(buf['buf'])
            if idf in short:
                 for (lenX, msg, bus, mod), cnt in short[idf].items():
                    if self.is_ascii(msg):
                        data_ascii = self.ret_ascii(msg)
                    else:
                        data_ascii = "  "
                    rows.append([str(bus),hex(idf), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(idf, msg), str(cnt)])
        cols = list(zip(*rows))
        col_widths = [max(len(value) for value in col) for col in cols]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += "\n"
        return table

    def print_dump_diff(self, def_in,name):
        return self.print_dump_diff_(name, 0)

    def print_dump_diff_id(self, def_in,name):
        return self.print_dump_diff_(name, 1)

    def print_dump_diff_(self, name, mode = 0):
        inp = name.split(",")
        if len(inp) == 4:
            name = inp[0].strip()
            idx1 = int(inp[1])
            idx2 = int(inp[2])
            rang = int(inp[3])
        elif len(inp) == 3:
            name = inp[0].strip()
            idx1 = int(inp[1])
            idx2 = int(inp[2])
            rang = 8 * 256
        else:
            name = inp[0].strip()
            idx2 = self._index
            idx1 = self._index - 1 if self._index - 1 >=0 else 0
            rang = 8 * 256

        table1 = self.create_short_table(self.all_frames[idx1]['buf'])
        table2 = self.create_short_table(self.all_frames[idx2]['buf'] + self.all_frames[idx1]['buf'])
        try:
            _name = open(name, 'w')
            for can_msg in self.all_frames[idx2]['buf']:
                if can_msg.CANFrame.frame_id not in list(table1.keys()):
                    _name.write(str(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + self.get_hex(can_msg.CANFrame.frame_raw_data) + "\n")
                elif mode == 0 and len(table2[can_msg.CANFrame.frame_id]) <= rang:
                    neq = True
                    for (len2, msg, bus, mod), cnt in table1[can_msg.CANFrame.frame_id].items():
                        if msg == can_msg.CANFrame.frame_raw_data:
                            neq = False
                    if neq:
                        _name.write(hex(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + self.get_hex(can_msg.CANFrame.frame_raw_data) + "\n")
            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def do_dump_replay(self, def_in, name):
        inp = name.split(",")
        if len(inp) == 2:
            name = inp[0].strip()
            idx1 = int(inp[1])
        else:
            name = inp[0].strip()
            idx1 = self._index
        try:
            _name = open(name, 'w')
            for can_msg in self.all_frames[idx1]['buf']:
                _name.write(hex(can_msg.CANFrame.frame_id) + ":" + str(can_msg.CANFrame.frame_length) + ":" + self.get_hex(can_msg.CANFrame.frame_raw_data) + "\n")
            _name.close()
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()


    def do_dump_csv(self, def_in, name):
        inp = name.split(",")
        if len(inp) == 2:
            name = inp[0].strip()
            idx1 = int(inp[1])
        else:
            name = inp[0].strip()
            idx1 = self._index
        self._bodyList = self.create_short_table(self.all_frames[idx1]['buf'])
        try:
            _name = open(name.strip(), 'w')
            _name.write("BUS,ID,LENGTH,MESSAGE,ASCII,COMMENT,COUNT\n")
            for fid, lst in self._bodyList.items():
                for (len, msg, bus, mod), cnt in lst.items():
                    if self.is_ascii(msg):
                        data_ascii = '"' + self.ret_ascii(msg) + '"'
                    else:
                        data_ascii = ""
                    _name.write(
                        str(bus) + "," + hex(fid) + "," + str(len) + "," + self.get_hex(msg) + ',' + data_ascii + ',' +\
                        "\"" + self.get_meta_descr(fid, msg) + "\"" + ',' + str(cnt) + "\n"
                    )
        except Exception as e:
            self.dprint(2, "can't open log")
            return str(e)
        return "Saved into " + name.strip()

    def print_diff(self, def_in, inp = ""):
        inp = inp.split(",")
        if len(inp) == 3:
            idx1 = int(inp[0])
            idx2 = int(inp[1])
            rang = int(inp[2])
        elif len(inp) == 2:
            idx1 = int(inp[0])
            idx2 = int(inp[1])
            rang = 8 * 256
        else:
            idx2 = self._index
            idx1 = self._index - 1 if self._index - 1 >=0 else 0
            rang = 8 * 256
        return self.print_diff_orig(0, idx1, idx2, rang)

    def print_diff_id(self, def_in, inp = ""):
        inp = inp.split(",")
        if len(inp) != 2:
            idx2 =  self._index
            idx1 =  self._index - 1 if self._index - 1 >= 0 else 0
        else:
            idx2 = int(inp[1])
            idx1 = int(inp[0])
        return self.print_diff_orig(1, idx1, idx2, 8 * 256)

    def print_diff_orig(self, mode, idx1, idx2, rang):

        table1 = self.create_short_table(self.all_frames[idx1]['buf'])
        table2 = self.create_short_table(self.all_frames[idx2]['buf'])
        table3 = self.create_short_table(self.all_frames[idx1]['buf'] + self.all_frames[idx2]['buf'])
        table = " DIFF sets between " + self.all_frames[idx1]['name'] + " and " + self.all_frames[idx2]['name'] + "\n"
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        for fid2, lst2 in table2.items():
            if fid2 not in list(table1.keys()):

                for (lenX, msg, bus, mod), cnt in lst2.items():
                    if self.is_ascii(msg):
                        data_ascii = self.ret_ascii(msg)
                    else:
                        data_ascii = "  "
                    rows.append([str(bus),hex(fid2), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid2, msg), str(cnt)])
            elif mode == 0 and len(table3[fid2]) <= rang:
                for (lenX, msg, bus, mod), cnt in lst2.items():

                    if (lenX, msg, bus, mod) not in  table1[fid2]:
                        if self.is_ascii(msg):
                            data_ascii = self.ret_ascii(msg)
                        else:
                            data_ascii = "  "
                        rows.append([str(bus),hex(fid2), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid2, msg), str(cnt)])

        cols = list(zip(*rows))
        col_widths = [max(len(value) for value in col) for col in cols]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += "\n"
        return table

    def new_diff(self, def_in, name = ""):
        _name = name.strip()
        _name = _name if _name != "" else "buffer_" + str(len(self.all_frames)-1)
        self._index += 1
        self.all_frames.append({'name':_name,'buf':[]})
        return "New buffer  " + _name + ", index: " + str(self._index) + " enabled and active"

    def do_print(self, def_in, index = "-1"):
        _index = int(index)
        temp_buf = []
        if _index == -1:
            for buf in self.all_frames:
                temp_buf = temp_buf + buf['buf']
        else:
            temp_buf = self.all_frames[_index]['buf']
        self._bodyList = self.create_short_table(temp_buf)
        table = "\n"
        rows = [['BUS', 'ID', 'LENGTH', 'MESSAGE', 'ASCII', 'DESCR', 'COUNT']]
        # http://stackoverflow.com/questions/3685195/line-up-columns-of-numbers-print-output-in-table-format
        for fid, lst in self._bodyList.items():
            for (lenX, msg, bus, mod), cnt in lst.items():
                if self.is_ascii(msg):
                    data_ascii = self.ret_ascii(msg)
                else:
                    data_ascii = "  "
                rows.append([str(bus),hex(fid), str(lenX), self.get_hex(msg), data_ascii, self.get_meta_descr(fid, msg), str(cnt)])

        cols = list(zip(*rows))
        col_widths = [ max(len(value) for value in col) for col in cols ]
        format_table = '    '.join(['%%-%ds' % width for width in col_widths ])
        for row in rows:
            table += format_table % tuple(row) + "\n"
        table += ""
        return table

    def do_clean(self, def_in):
        self.all_frames = [{'name':'start_buffer','buf':[]}]
        self._index = 0
        return "Buffers cleaned!"

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if can_msg.CANData:
            self.all_frames[self._index]['buf'].append(can_msg)
        return can_msg
