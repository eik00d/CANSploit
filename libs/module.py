import threading
import collections
import codecs
'''
Generic class for modules
'''


# Generic class for all modules
class CANModule:
    name = "Abstract CANSploit module"
    help = "No help available"
    id = 0
    version = 0.0

    _active = True  # Enabled/Disabled
    thr_block = threading.Event()  # Blocking mode (using events)

    @staticmethod
    def get_hex(bytes_in):
        return (codecs.encode(bytes_in, 'hex_codec')).decode("ISO-8859-1")

    @property
    def is_active(self):
        return self._active

    def get_status(self, def_in = 0):
        return "Current status: " + str(self._active)

    def do_activate(self, def_in = 0, mode = -1):
        if mode == -1:
            self._active = not self._active
        elif mode == 0:
            self._active = False
        else:
            self._active = True
        return "Active status: " + str(self._active)

    def dprint(self, level, msg):
        str_msg = self.__class__.__name__ + ": " + msg
        if level <= self.DEBUG:
            print(str_msg)

    def raw_write(self, string):  # Used for direct input
        ret = ""
        self.thr_block.wait(3)
        self.thr_block.clear()
        if string[0] in self._cmdList:
            cmd = self._cmdList[string[0]]
            if cmd[4]:
                if len(cmd) == 5:
                    cmd.append(0)
                if len(string.strip()) > 2:
                    ret = cmd[3](cmd[5],string[2:])
                else:
                    ret = cmd[3](cmd[5])
            else:
                ret = "Error: command is disabled!"
        self.thr_block.set()
        return ret

    def do_effect(self, can_msg, args):  # Effect (could be fuzz operation, sniff, filter or whatever)
        return can_msg

    def get_name(self):
        return self.name

    def get_help(self):
        return self._cmdList

    def __init__(self, params):

        self.DEBUG = int(params.get('debug', 0))
        self._bus = params.get('bus', self.__class__.__name__)
        self._active = False if params.get('active') in ["False", "false", "0", "-1"] else True
        self._cmdList = collections.OrderedDict()  # Command list (doInit section)
        self._cmdList['S'] = ["Current status", 0, "", self.get_status, True]
        self._cmdList['s'] = ["Stop/Activate current module", 0, "", self.do_activate, True]
        self._status = 0
        self.do_init(params)

    def get_status_bar(self):
        self.thr_block.wait(3)
        self.thr_block.clear()
        status = int(self._status)
        self.thr_block.set()
        return status

    def do_init(self, params):  # Call for some pre-calculation
        return 0

    def do_stop(self, params):  # Stop activity of this module
        return 0

    def do_start(self, params):  # Start activity of this module
        return 0

    def do_read(self, params):
        return 0

    def do_write(self, params):
        return 0
