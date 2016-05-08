from libs.module import *
from libs.can import *
from random import shuffle


class mod_fuzz1(CANModule):
    name = "Fuzzing one byte with chosen shift of CAN message"
    help = """
    
    This module doing one-byte fuzzing for chosen shift in data.
    
    Init parameters:  None
    
    Module parameters: 
    
      'fuzz'  - list of ID that should be fuzzed
      'nfuzz' - list of ID that should not be filtered
      'byte'  - byte index form 1 to 8, that should be fuzzed
      
      Example: {'fuzz':[133,111],'byte':1}

    """

    _i = 0
    fzb = []
    id = 2
    _active = True
    version = 1.0

    def counter(self):
        if self._i >= 255:
            self._i = 0

        self._i += 1
        return self._i - 1

    def do_init(self, params):
        for i in range(0, 255):
            self.fzb.append(i)

    # Change one byte to random        
    def do_fuzz(self, can_msg, shift):
        if 0 < shift < 9:
            can_msg.CANFrame.frame_data[shift - 1] = self.fzb[self.counter()]
            can_msg.CANFrame.parse_params()
            self.dprint(2, "Message " + str(can_msg.CANFrame.frame_id) +
                        " has been fuzzed (BUS = " + str(can_msg.bus) + ")")

        return can_msg

    def do_start(self, params):
        self._i = 0
        shuffle(self.fzb)

    # Effect (could be fuzz operation, sniff, filter or whatever)
    def do_effect(self, can_msg, args):
        if can_msg.CANData and can_msg.CANFrame.frame_type == CANMessage.DataFrame:
            if can_msg.CANFrame.frame_id in args.get('fuzz', []) and 'byte' in args:
                can_msg = self.do_fuzz(can_msg, args['byte'])
                can_msg.bus = self._bus
            elif 'nfuzz' in args and can_msg.CANFrame.frame_id not in args.get('nfuzz', []) and 'byte' in args:
                can_msg = self.do_fuzz(can_msg, args['byte'])
                can_msg.bus = self._bus
        return can_msg
