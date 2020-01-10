#!/usr/bin/env python3

## 
#  Emulator Settings
#  Resolution : 1024x720 240 HDPI
#  Android Version : 6.0
##

from modules.sortie import Sortie

class Main:
    def __init__(self):
        self.sortie_module = Sortie()
    def start(self):
        self.sortie_module.start()

if __name__ == '__main__':
    while True:
        azurpy = Main()
        azurpy.start()
        print("done")
