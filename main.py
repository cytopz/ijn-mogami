#!/usr/bin/env python3

######################################
#   Emulator Settings                #
#   Resolution : 1024x720 240 HDPI   #
#   Android Version : 6.0            #
######################################

import sys
from modules.sortie import Sortie
from modules.dialy import Dialy
from modules.raid import Raid
from utils.tools import Tools, Buttons
from utils.arg import args, parser

class Main:
    def __init__(self):
        self.dialy = args.dialy
        self.sortie_map = args.sortie
        self.manual = args.manual
        self.sortie_module = None
        self.raid_module = Raid('hard')
        self.dialy_module = Dialy()
        self.time_start = Tools.time_now()
        try:
            if not (self.manual or any(chr.isalpha() for chr in self.sortie_map)):
                self.go_home()
        except TypeError:
            self.go_home()

    def go_home(self):
        print('Starting...')
        if not Tools.find('battle_home'):
            Tools.tap(Buttons['home'])

    def start(self):
        if self.sortie_map:
            self.sortie_module = Sortie(self.sortie_map)
            self.sortie_module.start()
        elif self.dialy:
            self.dialy_module.start()
            self.print_time_elapsed()
            sys.exit(1)
        elif self.manual:
            print('waiting to enter map...')
            while not Tools.find('attack'):
                Tools.wait(1)
            input('entered map. press any key to continue.')
            self.sortie_module = Sortie(kill_req=args.manual)
            self.sortie_module.start()

    def print_time_elapsed(self):
        print(f'Done. Finished in {Tools.time_elapsed(Tools.time_now(), self.time_start)}')

if __name__ == '__main__':
    if not (args.dialy or args.sortie or args.manual):
        parser.error('no argument specified')
    try:
        mogami = Main()
        while True:
            mogami.start()
            mogami.print_time_elapsed()
            Tools.wait(5)
    except KeyboardInterrupt:
        print('\nExiting...')
        mogami.print_time_elapsed()
        sys.exit(0)
