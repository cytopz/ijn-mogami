from utils.tools import Dimension, Tools

class Raid:
    def __init__(self, diff):
        self.diff = diff
        self.buttons = {
            'ex': Dimension(922, 178),
            'hard': Dimension(922, 278),
            'normal': Dimension (922, 378),
            'easy': Dimension (922, 278),
            'go': Dimension(867, 566),
            'battle': Dimension(916, 584),
            'confirm_battle': Dimension(860, 600)
        }

    def start(self):
        while True:
            Tools.tap(self.buttons[self.diff])
            Tools.tap(self.buttons['go'])
            Tools.tap(self.buttons['battle'])
            while not Tools.find('touch_to_continue'):
                Tools.wait(5)
            Tools.tap(Dimension(785, 621))
            Tools.tap(Dimension(785, 621))
            Tools.tap(self.buttons['confirm_battle'])
            Tools.wait(3)
