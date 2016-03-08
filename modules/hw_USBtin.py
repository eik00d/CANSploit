from libs.can import *
from libs.module import *
import serial
import serial.tools.list_ports
import time


class hw_USBtin(CANModule):
    name = "USBtin I/O"
    help = """
    
    This module to read/write with USBtin http://www.fischl.de/usbtin/
    This device support only 1 bus, so for MITM u need one more device.
    Supporting for extended format!
    
    Init parameters example:  
    
    [hw_USBtin]
    port = auto         ; Serial port
    debug = 2           ; debug level (default 0)
    speed = 50         ; bus speed (500, 1000)

        
    Module parameters: 
      action - read or write. Will write/read to/from bus
      pipe -  integer, 1 or 2 - from which pipe to read or write 
          If you use both buses(and different), than you need only one pipe configured...
        
        Example: {'action':'read','pipe':2} 
   
    """

    _serialPort = None
    _COMPort = None
    _speed = {500: 'S6\r', 1000: 'S8\r', 10: 'S0\r', 100: 'S3\r', 50: 'S2\r'}
    _currentSpeed = 10
    version = 1.0

    id = 6

    _bus = 60

    def get_info(self):  # Read info
        self._serialPort.write("S0\r")
        time.sleep(1)
        self._serialPort.write("V\r")
        time.sleep(1)
        return self.read_all()

    def read_all(self):
        out = ""
        while self._serialPort.inWaiting() > 0:
            out += self._serialPort.read(1)
        return out

    def do_stop(self, params):  # disable reading
        self._serialPort.write("C\r")
        time.sleep(1)
        self.read_all()

    def do_start(self, params):  # enable reading
        self._serialPort.write(self._speed[self._currentSpeed] + "\r")
        time.sleep(1)
        self._serialPort.write("O\r")
        time.sleep(1)

    def init_port(self):
        try:
            self._serialPort = serial.Serial(self._COMPort, 57600, timeout=0.5, parity=serial.PARITY_EVEN, rtscts=1)

            if (self.get_info().find("V0100")) != -1:
                self.dprint(1, "Port found: " + self._COMPort)
                return 1
            else:
                self.dprint(1, "Device not found: " + self._COMPort)
                self._serialPort.close()
                return 0
        except:
            self.dprint(0, 'Error opening port: ' + self._COMPort)
            return 0

    def do_init(self, params={}):  # Get device and open serial port
        # Interactive mode
        if 'debug' in params:
            self.DEBUG = int(params['debug'])

        self.dprint(1, "Init phase started...")

        if 'port' in params:
            self._COMPort = params['port']
            if params['port'] == 'auto':
                for port in list(serial.tools.list_ports.comports()):
                    self._COMPort = port[0]
                    if self.init_port() == 1:
                        break
                if not self._serialPort:
                    self.dprint(0, 'Can\'t init device!')
                    exit()
            else:
                self.init_port()
                exit()
        else:
            self.dprint(0, 'No port in config!')
            return 0

        self.do_stop(params)
        # data=self.readAll()
        self._currentSpeed = int(params.get('speed', 500))

        # print str(self._serialPort)
        self.dprint(1, "PORT: " + self._COMPort)
        self.dprint(1, "Speed: " + str(self._currentSpeed))
        self.dprint(1, "USBtin device found!")

        self._cmdList['t'] = ["Send direct command to the device, like t0010411223344", 1, " <cmd> ", self.dev_write]

    def dev_write(self, data):
        self.dprint(1, "CMD: " + data)
        self._serialPort.write(data + "\r")
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
        data = ""
        if self._serialPort.inWaiting() > 0:
            while not can_msg.CANData and not can_msg.debugData:
                byte = self._serialPort.read(1)
                # print byte
                if byte == "":
                    break

                data += byte
                if data[-1:] == "\r":
                    can_msg.bus = self._bus  # Bus USBtin as BUS 60...
                    if data[0] == "t":
                        # "t10F81122334455667788"
                        _length = int(data[4])
                        _id = struct.unpack("!H", ("0" + data[1:4]).decode('hex'))[0]
                        _data = [struct.unpack("B", x)[0] for x in data[5:-1].decode('hex')]

                        can_msg.CANFrame = CANMessage(_id, _length, _data, False, CANMessage.DataFrame)

                        can_msg.CANData = True

                    elif data[0] == "T":  # Extended
                        # "T0011111181122334455667788"
                        _length = int(data[9])
                        _id = struct.unpack("!I", (data[1:9]).decode('hex'))[0]
                        _data = [struct.unpack("B", x)[0] for x in data[10:-1].decode('hex')]

                        can_msg.CANFrame = CANMessage(_id, _length, _data, True, CANMessage.DataFrame)
                        can_msg.CANData = True

                    elif data[0] == "r":  # RTR
                        _length = int(data[4])
                        _id = struct.unpack("!H", ("0" + data[1:4]).decode('hex'))[0]

                        can_msg.CANFrame = CANMessage(_id, _length, [], False, CANMessage.RemoteFrame)
                        can_msg.CANData = True

                    elif data[0] == "R":  # Extended RTR
                        _length = int(data[9])
                        _id = struct.unpack("!I", (data[1:9]).decode('hex'))[0]

                        can_msg.CANFrame = CANMessage(_id, _length, [], True, CANMessage.RemoteFrame)
                        can_msg.CANData = True
                    elif data[0] == 'z' or data[0] == 'Z' or data[0] == "\r" or data[0] == "\x07":
                        break
                    else:
                        can_msg.debugData = True
                        can_msg.debugText = {'text': data}

                    self.dprint(2, "USBtin READ: " + data)

        return can_msg

    def do_write(self, can_msg):
        if can_msg.CANData:
            cmd_byte = None
            if not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:  # 11 bit format
                cmd_byte = "t"
            elif can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.DataFrame:
                cmd_byte = "T"
            elif not can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.RemoteFrame:
                cmd_byte = "r"
            elif can_msg.CANFrame.frame_ext and can_msg.CANFrame.frame_type == CANMessage.RemoteFrame:
                cmd_byte = "R"
            if cmd_byte:
                write_buf = cmd_byte + can_msg.CANFrame.frame_raw_id.encode('hex')[1:] + \
                    str(can_msg.CANFrame.frame_length) + can_msg.CANFrame.frame_raw_data.encode('hex') + "\r"
                self._serialPort.write(write_buf)
                self.dprint(2, "WRITE: " + write_buf)
        return can_msg
