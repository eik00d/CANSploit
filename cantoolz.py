from optparse import OptionParser
from libs.engine import *
import re


######################################################
#                                                    # 
# CANSploit v 0.9b                                   #
#             ... or can't?                          #
######################################################
#      Main Code Monkey    Alyosha Sintsov           #
#                              aka @asintsov         #
#      alex.sintsov@gmail.com                        #
######################################################
#                                                    #
# Want to be there as contributor?                   #
# Help us here: https://github.com/eik00d/CANSploit  #
#                                                    #
########### MAIN CONTRIBUTORS ########################
# - Boris Ryutin ( @dukebarman )                     #
#      Fist supporter and awesome guy                #
######################################################
# We need:                                           #
#    - more hardware to support                      #
#    - unit tests                                    # 
#    - new modules!                                  #
#    - testers!                                      #
#    - GUI... so original                            #
#    - doc writes                                    #
#    - bug fixers 8)                                 #
#                                                    #
#    With support of DEF CON RUSSIA                  #
#    https://defcon-russia.ru                        #
#                                                    #
######################################################


def start(self):
    # try:
    self.load_config()
    # except:
    #    self.dprint(0,"Config syntax error")
    self.main_loop()


# UI class


class UserInterface:
    def __init__(self):
        usage = "%prog [options] for more help: %prog -h"
        parser = OptionParser(usage)

        parser.add_option("--debug", "-d", action="store", dest="DEBUG", type="int", help="Debug level")
        parser.add_option("--config", "-c", action="store", dest="CONFIG", type="string",
                          help="load config from file")
        parser.add_option("--gui", "-g", action="store", dest="GUI", type="string",
                          help="GUI mode, c - console or w - web (not implemented yet)")

        [options, args] = parser.parse_args()  # TODO need args?

        if options.DEBUG:
            self.DEBUG = options.DEBUG
        else:
            self.DEBUG = 0

        if options.CONFIG:
            self.CONFIG = options.CONFIG
        else:
            self.CONFIG = None

        if options.GUI:
            self.GUI = options.CONFIG
        else:
            self.GUI = "console"

        self.CANEngine = CANSploit()

        if self.CONFIG:
            self.CANEngine.load_config(self.CONFIG)

        if self.GUI[0] == "c":
            self.console_loop()
        elif self.GUI[0] == "w":
            self.web_loop()
        else:
            print("No such GUI...")

    def loop_exit(self):
        exit()

    def web_loop(self):
        print("WEB UI is not implemented")

    def console_loop(self):
        while True:
            try:
                input = raw_input(">> ")
            except KeyboardInterrupt:
                input = "stop"

            if input == 'q' or input == 'quit':
                self.CANEngine.stop_loop()
                self.loop_exit()
            elif input == 'start' or input == 's':
                self.CANEngine.start_loop()

            elif input == 'stop' or input == 's':
                self.CANEngine.stop_loop()

            elif input == 'view' or input == 'v':
                print("Loaded queue of modules: ")
                modz = self.CANEngine.get_modules_list()
                total = len(modz)
                i = 0
                print
                for name, module, params, pipe in modz:
                    tab1 = "\t"
                    tab2 = "\t"
                    tab1 += "\t" * (28 / len(str(name)))
                    tab2 += "\t" * (28 / len(str(params)))
                    print("Module " + name + tab1 + str(params) + tab2 + "Enabled: " + str(module.is_active))
                    if i < total - 1:
                        print("\t||\t")
                        print("\t||\t")
                        print("\t\/\t")
                    i += 1

            elif input[0:5] == 'edit ' or input[0:2] == 'e ':  # edit params from the console
                match = re.match(r"(edit|e)\s+([\w\!\~]+)\s+(.*)", input, re.IGNORECASE)
                if match:
                    module = match.group(2).strip()
                    _paramz = match.group(3).strip()
                    try:
                        paramz = ast.literal_eval(_paramz)
                        self.CANEngine.edit_module(str(module), paramz)
                        print("Edited module: " + str(module))
                        print("Added  params: " + str(self.CANEngine.get_module_params(module)))
                    except Exception as e:
                        print("Edit error: " + str(e))
                else:
                    print("Wrong format for EDIT command")

            elif input[0:4] == 'cmd ' or input[0:2] == 'c ':
                match = re.match(r"(cmd|c)\s+([\w~!]+)\s+(.*)", input, re.IGNORECASE)
                if match:
                    _mod = str(match.group(2).strip())
                    _paramz = match.group(3).strip()
                    if 1 == 1:
                        #                    try:
                        text = self.CANEngine.call_module(_mod, str(_paramz))
                        print(text)
                        #                    except Exception as e:
                        #                        print "CMD input error: "+str(e)

            elif input == 'help' or input == 'h':
                print
                print('start\t\tStart sniff/mitm/fuzz on CAN buses')
                print('stop or ctrl+c\tStop sniff/mitm/fuzz')
                print('view\t\tList of loaded MiTM modules')
                print('edit <module> [params]\t\tEdit parameters for modules')
                print('cmd <cmd>\t\tSend some cmd to modules')
                print('help\t\tThis menu')
                print('quit\t\tClose port and exit')
                print


def main():
    sys.dont_write_bytecode = True
    UserInterface()


if __name__ == '__main__':
    main()
