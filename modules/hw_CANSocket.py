from libs.can import *
from libs.module import *
import socket
import struct

class hw_CANSocket(CANModule):
    name = "CANSocket I/O"
    help = """
    
    This module to read/write with CANSocket

    
    Init parameters example:  

     'iface' : 'vcan0',       # device

    Module parameters: 
      action - 'read' or 'write'. Will write/read to/from bus
      'pipe' -  integer, 1 by default - from which pipe to read or write

        Example: {'action':'read','pipe':2}
   
    """

    socket = None
    device = None


    def do_init(self, init_params):  # Get device and open serial port
        self.device = init_params.get('iface', None)
        self._bus = init_params.get('bus','CANSocket')
        self._cmdList['t'] = ["Send CAN frame directly, like 01A#11223344", 1, " <frame> ", self.dev_write, True]
        self._active = True
        self._run = False

    def dev_write(self, def_in, data):
        self.dprint(1, "CMD: " + data)
        if self._run:
            idf, dataf = data.strip().split('#')
            dataf = bytes.fromhex(dataf)
            idf = int(idf, 16)
            lenf = min(8, len(dataf))
            message = CANSploitMessage()
            message.CANData = True
            message.CANFrame = CANMessage.init_data(idf, lenf, dataf[0:lenf])
            self.do_write(message)
        return ""

    def do_start(self, params):
        if self.device and not self._run:
            try:
                self.socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW,  socket.CAN_RAW)
                self.socket.setblocking(0)
                self.socket.bind((self.device,))
                self._run = True
            except Exception as e:
                self._run = False
                self.dprint(0, "ERROR: " + str(e))

    def do_stop(self, params):
        if self.device and self._run:
            try:
                self.socket.close()
                self._run = False
            except Exception as e:
                self._run = False
                self.dprint(0, "ERROR: " + str(e))

    def do_effect(self, can_msg, args):  # read full packet from serial port
        if args.get('action') == 'read':
            can_msg = self.do_read(can_msg)
        elif args.get('action') == 'write':
            self.do_write(can_msg)
        else:
            self.dprint(1, 'Command ' + args['action'] + ' not implemented 8(')
        return can_msg

    def do_read(self, can_msg):
        if self._run and not can_msg.CANData:
            try:
                can_frame = self.socket.recv(16)
                self.dprint(2, "READ: " + self.get_hex(can_frame))
                if len(can_frame) == 16:
                    can_msg.CANData = True
                    idf = struct.unpack("I", can_frame[0:4])[0]
                    if idf & 0x80000000:
                        idf &= 0x7FFFFFFF
                    can_msg.CANFrame = CANMessage.init_data(idf, can_frame[4], can_frame[8:8+can_frame[4]])
                    can_msg.bus = self._bus
            except:
                return can_msg
        return can_msg

    def do_write(self, can_msg):
        if can_msg.CANData:
            idf = can_msg.CANFrame.frame_id
            if can_msg.CANFrame.frame_ext:
                idf |= 0x80000000
            data = struct.pack("I", idf) + struct.pack("B", can_msg.CANFrame.frame_length)+ b"\xff\xff\xff" + can_msg.CANFrame.frame_raw_data[0:can_msg.CANFrame.frame_length] + b"0"*(8-can_msg.CANFrame.frame_length)
            self.socket.send(data)
            self.dprint(2, "WRITE: " + self.get_hex(data))
        return can_msg
