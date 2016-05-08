from libs.can import *
from libs.module import *


class hw_fakeIO(CANModule):
    name = "test I/O"
    help = """
    
    This module using for fake reading and writing CAN messages.
    No physical canal required. Used for tests. 
    
    Init parameters example:  

    Module parameters: 
      action - read or write. Will write/read to/from bus
      pipe -  integer, 1 or 2 - from which pipe to read or write 
          If you use both buses(and different), than you need only one pipe configured...
        
          Example: {'action':'read','pipe':2}
   
    """

    version = 1.0
    CANList = None
    _bus = 30

    def do_start(self, params):
        self.CANList = None

    def do_stop(self, params):  # disable reading
        self.CANList = None

    def do_init(self, params):  # Get device and open serial port
        self._cmdList['t'] = ["Send direct command to the device, like 13:8:1122334455667788", 1, " <cmd> ",
                              self.dev_write, True]
        return 1

    def dev_write(self, def_in, line):
        self.dprint(0, "CMD: " + line)
        fid = line.split(":")[0]
        length = line.split(":")[1]
        data = line.split(":")[2]
        self.CANList = CANMessage.init_data(int(fid), int(length), bytes.fromhex(data)[:8])
        return ""

    def do_effect(self, can_msg, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can_msg = self.do_read(can_msg)
        elif args.get('action') == 'write':
            self.do_write(can_msg)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
        return can_msg

    def do_read(self, can_msg):
        if self.CANList:
            can_msg.CANData = True
            can_msg.CANFrame = self.CANList
            can_msg.bus = self._bus
            self.CANList = None
            self.dprint(2, "Got message!")
        return can_msg

    def do_write(self, can_msg):
        if can_msg.CANData:
            self.CANList = can_msg.CANFrame
            self.dprint(2, "Wrote message!")
        return can_msg
