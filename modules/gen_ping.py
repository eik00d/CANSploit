from libs.module import *
from libs.uds import *
import time

class gen_ping(CANModule):
    name = "Sending CAN pings"
    help = """
    
    This module doing ID buteforce.
    (combine with mod_stat for example)
    Init parameters: None
    Module parameters:  
       body           -  data HEX that will be used in CAN for discovery (by default body is 0000000000000000)
       mode           -  by default CAN, but also support ISOTP and UDS
       range          -  [0,1000] - ID range
       delay          - delay between frames (0 by default)
         {'body':'0011223344556677889900aabbccddeeff','mode':'isotp'}  ; ISO-TP
         {'body':'001122334455667788','mode':'CAN'}  ; ISO-TP
         {'services':[{'service':0x01, 'sub':0x0d},{'service':0x09, 'sub':0x02},{'service':0x2F, 'sub':0x03, 'data':[7,3,0,0]}],'mode':'UDS'}  ; UDS
    """

    queue_messages = []

    def do_init(self, params):
        self._active = False
        self._last = 0
        self._full = 1

    def get_status(self, def_in):
        return "Current status: " + str(self._active) + "\nFrames in queue: " + str(len(self.queue_messages))

    def do_ping(self, params):
        if not self.queue_messages:
            self._active = False
            self.do_start(params)
            return None

        return self.queue_messages.pop()

    def do_start(self, args):
        self.queue_messages = []
        self.last = time.clock()
        if 'body' in args:
            try:
                _data = list(bytes.fromhex(args['body']))
            except:
                _data = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            _data = [0, 0, 0, 0, 0, 0, 0, 0]

        # 0 - CAN, 1 - ISO-TP, 2 - UDS
        iso_mode = 1 if args.get('mode') in ['ISO', 'iso', 'ISOTP', 'isotp'] else\
            2 if args.get('mode') in ['uds', 'UDS'] else 0

        padding = args.get('padding', None)
        shift = int(args.get('shift', 0x8))

        if 'range' in args and int(args['range'][0]) < int(args['range'][1]):
            for i in range(int(args['range'][0]), int(args['range'][1])):
                if iso_mode == 1:
                    iso_list = ISOTPMessage.generate_can(i, _data, padding)
                    iso_list.reverse()
                    self.queue_messages.extend(iso_list)
                elif iso_mode == 0:
                    self.queue_messages.append(CANMessage.init_data(i, len(_data), _data[:8]))
                elif iso_mode == 2:
                    if 'services' in args:
                        for service in args['services']:
                            if 'service' in service:
                                uds_m = UDSMessage(shift, padding)
                                if 'sub' in service:
                                    sub = service['sub']
                                elif service['service'] in UDSMessage.services_base:
                                    subs = UDSMessage.services_base[service['service']]
                                    sub = 0
                                    for s in subs:
                                        sub = list(s.keys())[0]
                                        if not sub:
                                            sub = 0
                                            continue
                                        else:
                                            break
                                else:
                                    sub = 0
                                if 'data' in service:
                                    dat = service['data']
                                else:
                                    dat = []
                                iso_list = uds_m.add_request(i, service['service'], sub, dat)
                                iso_list.reverse()
                                self.queue_messages.extend(iso_list)
        else:
            self.dprint(1, "No range specified")
            self._active = False
        self._full = len(self.queue_messages)
        self._last = 0


    def do_effect(self, can_msg, args):
        d_time = float(args.get('delay', 0))
        if not can_msg.CANData:
            if d_time > 0:
                if time.clock() - self.last >= d_time:
                    self.last = time.clock()
                    can_msg.CANFrame = self.do_ping(args)

                else:
                    can_msg.CANFrame = None
            else:
                can_msg.CANFrame = self.do_ping(args)

            if can_msg.CANFrame and not can_msg.CANData:
                can_msg.CANData = True
                can_msg.bus = self._bus
                self._last += 1
                self._status = self._last/(self._full/100.0)

        return can_msg
