from libs.module import *
from libs.isotp import *
import time


class gen_fuzz(CANModule):
    name = "Fuzzing one byte with shift (CAN), byte fuzz"
    help = """
    
    This module doing one-byte fuzzing for chosen shift in data.
    
    Init parameters:  None
    
    Module parameters: 

      'id'  - [0,1,2,111,333,[334,339]] - ID to fuzz. If list have sublist, than sublist should be a range
      'data'   - default data
      'delay'  - delay between frames (0 by default)
      'index'  - [1,4] - list of bytes (indexes) that should be fuzzed
      
      Example: {'id':[111,113],'data':[0,0,0,0,0,0,0,0],'delay':0}

    """

    _i = 0
    queue_messages = []


    version = 1.0

    def do_init(self, params):
        self._active = False
        self._last = 0
        self._full = 1

    def get_status(self):
        return "Current status: " + str(self._active) + "\nFrames in queue: " + str(len(self.queue_messages))

    def do_start(self, args):
        self._i = 0
        self.last = time.clock()
        self.queue_messages = []
        iso_mode = 1 if args.get('mode') in ['ISO', 'iso', 'ISOTP', 'isotp'] else 0
        if 'id' in args:
            for z in args['id']:
                if isinstance(z,list) and len(z)==2:
                    x = list(range(z[0], z[1]))
                elif isinstance(z, int):
                    x = [z]
                else:
                    break
                for i in x:
                    _body = list(args.get('data', []))
                    _i = 0
                    while _i < len(_body):
                        if _i in args.get('index', list(range(0, len(_body)))):
                            for byte in range(0, 256):
                                _body2 = list(args.get('data', []))
                                _body2[_i] = byte
                                if iso_mode == 1:
                                    iso_list = ISOTPMessage.generate_can(i, _body2)
                                    iso_list.reverse()
                                    self.queue_messages.extend(iso_list)
                                else:
                                    self.queue_messages.append(CANMessage.init_data(i, len(_body2), _body2[:8]))
                        _i += 1
        self._full = len(self.queue_messages)
        self._last += 0


    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if not self.queue_messages:
            self._active = False
            self.do_start(args)
        elif not can_msg.CANData:
            d_time = float(args.get('delay', 0))
            if d_time > 0:
                if time.clock() - self.last >= d_time:
                    self.last = time.clock()
                    can_msg.CANFrame = self.queue_messages.pop()
                    can_msg.CANData = True
                    can_msg.bus = self._bus
                    self._last += 1
                    self._status = self._last/(self._full/100.0)

            else:
                can_msg.CANFrame = self.queue_messages.pop()
                can_msg.CANData = True
                can_msg.bus = self._bus
                self._last += 1
                self._status = self._last/(self._full/100.0)

        return can_msg
