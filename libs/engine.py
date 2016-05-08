import sys
import threading
from libs.can import *


'''
Main class
'''


class CANSploit:
    DEBUG = 0
    ascii_logo_c = """

   _____          _   _ _______          _
  / ____|   /\   | \ | |__   __|        | |
 | |       /  \  |  \| |  | | ___   ___ | |____
 | |      / /\ \ | . ` |  | |/ _ \ / _ \| |_  /
 | |____ / ____ \| |\  |  | | (_) | (_) | |/ /
  \_____/_/    \_\_| \_|  |_|\___/ \___/|_/___|


"""

    def dprint(self, level, msg):
        if level <= self.DEBUG:
            print((self.__class__.__name__ + ": " + msg))

    def __init__(self):
        self._version = "0.9b"  # version
        self._enabledList = []  # queue of active modules with params
        self._pipes = {}  # two pipes with CANMessages
        self._type = {}  # Pointers on instances here
        self._modules = []  # loaded modules
        self._thread = None
        self._mainThread = None
        self._stop = threading.Event()
        self._stop.set()
        self._raw = threading.Event()
        self._idc = -1
        sys.path.append('./modules')
        sys.dont_write_bytecode = True

    # Main loop with two pipes
    def main_loop(self):
        # Run until STOP
        error_on_bus = {}
        error = False
        while not self._stop.is_set():
            self._pipes = {}
            i = 0
            for name, module, params in self._enabledList:  # Each module
                #  Handle CAN message

                if module.is_active:
                    module.thr_block.wait(3)
                    module.thr_block.clear()
                    if params['pipe'] not in self._pipes:
                        self._pipes[params['pipe']] = CANSploitMessage()

                    if error and error_on_bus.get(i, False):
                        self._pipes[params['pipe']] = module.do_effect(self._pipes[params['pipe']], params) # If error, try to fix
                    elif not error:
                        self._pipes[params['pipe']] = module.do_effect(self._pipes[params['pipe']], params) # doEffect on CANMessage

                    if self._pipes[params['pipe']].debugData and self._pipes[params['pipe']].debugText.get('do_not_send', False):
                        error_on_bus[i] = True
                        error = True
                        module.dprint(0,"BUS ERROR detected")
                        self._pipes[params['pipe']].debugData = False
                    elif self._pipes[params['pipe']].debugData and self._pipes[params['pipe']].debugText.get('please_send', False):
                        error_on_bus[i] = False
                        error = False
                        self._pipes[params['pipe']].debugData = False
                        module.dprint(0,"BUS ERROR fixed")
                    i += 1
                    module.thr_block.set()


                    # Here when STOP
        for name, module, params in self._enabledList:
            module.do_stop(params)

    # Call module command        
    def call_module(self, index, params):
        # x = self.find_module(mod)
        x = index
        if x >= 0:
            ret = self._enabledList[x][1].raw_write(params)
        else:
            ret = "Module " + str(index) + " not loaded!"
        return ret

    # Enable loop        
    def start_loop(self):
        self._stop.clear()

        for name, module, params in self._enabledList:
            module.do_start(params)
            params['!error_on_bus'] = False
            module.thr_block.set()

        self._thread = threading.Thread(target=self.main_loop)

        self._thread.daemon = True
        self._thread.start()

        return not self._stop.is_set()

    # Pause loop      
    def stop_loop(self):
        self._stop.set()
        return not self._stop.is_set()

    # Current status
    @property
    def status_loop(self):
        return not self._stop.is_set()

    # Having defulat values for id and pipe params
    def check_params(self, params):
        if 'pipe' not in list(params.keys()):
            params['pipe'] = 1
        return params

    # Add module and params to the end    
    def push_module(self, mod, params):
        chkd_params = self.check_params(params)
        self._enabledList.append([mod, self._type[mod.split("!")[0]], chkd_params])

    # Find index of module with name mod    
    def find_module(self, mod):
        i = 0
        x = -1
        for name, module, params in self._enabledList:
            if name == mod:
                x = i
                break
            i += 1
        return x

        # Add new params to module named mod

    def edit_module(self, index, params):
        # x = self.find_module(mod)
        x = index
        if x >= 0:
            chkd_params = self.check_params(params)
            self._enabledList[x][2] = chkd_params
            return x
        return -1

    # Get all modules and parameters    
    def get_modules_list(self):
        return self._enabledList

    # Get all parameters for module named mod    
    def get_module_params(self, index):
        # x = self.find_module(mod)
        x = index
        if x >= 0:
            return self._enabledList[x][2]
        return None

        # Load and init new module form lib

    def init_module(self, mod, params):
        namespace = {}
        self._modules.append(__import__(mod.split("~")[0]))
        namespace['mod'] = self._modules[-1]
        namespace['params'] = params
        exec('cls = mod.' + mod.split("~")[0] + '(params)', namespace)  # init module
        self._type[mod] = namespace['cls']

        # Load all modules and params form config file

    def load_config(self, fullpath):  # Load config from file
        fullpath = fullpath.replace('\\', '/')
        parts = fullpath.split("/")

        if len(parts)>1:
            path = '/'.join(parts[0:-1])
            sys.path.append(path)

        mod = parts[-1].split(".")[0]

        config = __import__(mod)

        for module, init_params in config.load_modules.items():
            self.init_module(module, init_params)

        for action in config.actions:
            self.push_module(list(action.keys())[0], list(action.values())[0])
        return 1
