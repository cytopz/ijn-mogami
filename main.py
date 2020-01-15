#!/usr/bin/env python3

######################################
#   Emulator Settings                #
#   Resolution : 1024x720 240 HDPI   #
#   Android Version : 6.0            #
######################################

import sys
from modules.sortie import Sortie
from utils.tools import Tools

class Main:
    def __init__(self):
        self.sortie_module = Sortie()
    def start(self):
        print('Starting sortie...')
        self.sortie_module.start()
    def print_time_elapse(self):
        print(f'Sortie finished at {self.sortie_module.get_time_elapse()}')

if __name__ == '__main__':
    try:
        while True:
            mogami = Main()
            mogami.start()
            mogami.print_time_elapse()
            Tools.wait(3)
    except KeyboardInterrupt:
            print('\nExiting...')
            sys.exit(0)
