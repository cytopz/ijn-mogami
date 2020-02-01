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
        self.sortie_module = None
        self.raid_module = Raid('hard')
        self.dialy_module = Dialy()
        self.time_start = Tools.time_now()
        self.dialy = args.dialy
        self.sortie = args.sortie

    def start(self):
        print('Starting....')
        if not Tools.find('battle_home'):
            Tools.tap(Buttons['home'])
        if self.sortie:
            self.sortie_module = Sortie(self.sortie)
            self.sortie_module.start()
        elif self.dialy:
            self.dialy_module.start()
            self.print_time_elapsed()
            sys.exit(1)

    def print_time_elapsed(self):
        print(f'Done. Finished in {Tools.time_elapsed(Tools.time_now(), self.time_start)}')

if __name__ == '__main__':
    if not (args.dialy or args.sortie):
        parser.error('no argument specified')
    try:
        while True:
            mogami = Main()
            mogami.start()
            mogami.print_time_elapsed()
            Tools.wait(3)
    except KeyboardInterrupt:
            print('\nExiting...')
            mogami.print_time_elapsed()
            sys.exit(0)

