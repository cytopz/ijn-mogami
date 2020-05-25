from utils.tools import Tools, Dimension, MapDetail, Buttons
from modules.sortie import Sortie

class Dialy:
    def __init__(self):
        self.hard_mode_map = '9-2'
        self.clear_mode = True
        self.dialy_level = '70'
        self.escort_dialy_mode = 'fire'
        self.today = Tools.time_now().strftime('%a').lower()
        self.chip_mission = False
        self.sortie_module = Sortie(self.hard_mode_map, True, self.clear_mode)

    def start(self):
        self.hard_mode()
        self.dialy_challenge()

    def hard_mode(self):
        if Tools.find('hard_mode'):
            Tools.tap(Buttons['hard_mode'])
        for _ in range(3):
            self.sortie_module.start()

    def dialy_challenge(self):
        banner_coord = []
        lvl_coord = None
        switched_fleet = False
        Tools.tap(Buttons['dialy'])
        Tools.wait(2)
        if self.today in ['wed', 'sat', 'sun']:
            banner_coord.append(Dimension(730, 350))
        if self.today in ['tue', 'fri', 'sun']:
            banner_coord.append(Dimension(300, 350))
        if self.today in ['mon', 'thu', 'sun']:
            banner_coord.append(Dimension(125, 350))
        for coord in banner_coord:
            Tools.tap(coord)
            Tools.tap(Dimension(512, 360))
            if self.today in ['mon', 'thu', 'sun']:
                lvl_coord = Buttons[f'dialy_{self.dialy_level}_{self.escort_dialy_mode}']
            else:
                lvl_coord = Buttons[f'dialy_{self.dialy_level}']
            for _ in range(3):
                Tools.tap(lvl_coord)
                if not switched_fleet:
                    for _ in range(5):
                        Tools.tap(Dimension(730, 360), 0.13)
                    switched_fleet = True
                self.sortie_module.start_battle()
            Tools.tap(Buttons['back'])
        Tools.tap(Buttons['home'])
