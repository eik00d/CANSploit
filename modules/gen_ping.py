from libs.module import *
from libs.uds import *


class gen_ping(CANModule):
    name = "Sending CAN pings"
    help = """
    
    This module doing ID buteforce.
    (combine with mod_stat for example)
    
   
    Module parameters:  
       body           -  data HEX that will be used in CAN for discovery (by default body is 0000000000000000)
       mode           -  by default CAN, but also support ISOTP and UDS
       range          -  [0,1000] - ID range
         {'body':'0011223344556677889900aabbccddeeff','mode':'isotp'}  ; ISO-TP
         {'body':'001122334455667788','mode':'CAN'}  ; ISO-TP
         {'services':[{'service':0x01, 'sub':0x0d},{'service':0x09, 'sub':0x02},{'service':0x2F, 'sub':0x03, 'data':[7,3,0,0]}],'mode':'UDS'}  ; UDS
    """
    _active = False
    queue_messages = []

    def do_ping(self):
        if not self.queue_messages:
            self._active = False
            return None

        return self.queue_messages.pop()

    def do_start(self, args):
        self.queue_messages = []
        if 'body' in args:
            try:
                _data = [struct.unpack("B", x)[0] for x in (args['body'].decode('hex'))]
            except:
                _data = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            _data = [0, 0, 0, 0, 0, 0, 0, 0]

        # 0 - CAN, 1 - ISO-TP, 2 - UDS
        iso_mode = 1 if args.get('mode') in ['ISO', 'iso', 'ISOTP', 'isotp'] else\
            2 if args.get('mode') in ['uds', 'UDS'] else 0

        if 'range' in args and int(args['range'][0]) < int(args['range'][1]):
            for i in range(int(args['range'][0]), int(args['range'][1])):
                if iso_mode == 1:
                    iso_list = ISOTPMessage.generate_can(i, _data)
                    iso_list.reverse()
                    self.queue_messages.extend(iso_list)
                elif iso_mode == 0:
                    self.queue_messages.append(CANMessage.init_data(i, len(_data), _data[:8]))
                elif iso_mode == 2:
                    if 'services' in args:
                        for service in args['services']:
                            if 'service' in service:
                                uds_m = UDSMessage()
                                if 'sub' in service:
                                    sub = service['sub']
                                elif service['service'] in UDSMessage.services_base:
                                    subs = UDSMessage.services_base[service['service']]
                                    sub = 0
                                    for s in subs:
                                        sub = s.keys()[0]
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

    def do_effect(self, can_msg, args):
        can_msg.CANFrame = self.do_ping()  # get frame

        if can_msg.CANFrame:
            can_msg.CANData = True
        else:
            can_msg.CANData = False

        return can_msg
