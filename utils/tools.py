import time
import subprocess
import cv2
import numpy as np
from datetime import datetime
from scipy import spatial
from utils.adb import Adb

class Dimension:
    def __init__(self, x, y, mob=False, siren=False):
        self.x = x
        self.y = y
        self.mob = mob
        self.siren = siren
        if mob:
            if siren:
                self.inc_y(40)
                self.inc_x(-5)
            self.inc_val(25)
            self.check_borders()

    def __eq__ (self, other):
        coord1 = self.x, self.y
        coord2 = other.x, other.y
        return spatial.distance.euclidean(coord1, coord2) < 10

    def __hash__(self):
        return hash((self.x, self.y, self.mob, self.siren))

    def __repr__(self):
        return f'({self.x}, {self.y})'

    def inc_x(self, val):
        self.x += val

    def inc_y(self, val):
        self.y += val

    def inc_val(self, val):
        self.inc_x(val)
        self.inc_y(val)

    def dec_val(self, val):
        self.inc_x(-val)
        self.inc_y(-val)

    def check_borders(self):
        if self.x < 98:
            delta = 98-self.x
            self.x += delta + 6
        if self.y > 640:
            delta = self.y - 640
            self.y -= delta + 6
        if self.x > 984:
            if self.y < 169 and self.y > 86:
                delta = 169 - self.y
                self.y += delta + 25

class Tools:

    DEBUG_MODE = False

    SIMILARITY_VALUE = 0.8
    CURRENT_SCREEN = np.array([[]])
    UPDATED = False

    @classmethod
    def update_screen(self, bgr=0):
        img = None
        while img is None:
            img = cv2.imdecode(np.fromstring(Adb.exec_out('screencap -p'), dtype=np.uint8), bgr)
        return img

    @classmethod
    def find(self, template, similarity=SIMILARITY_VALUE, mob=False, sortie_map=False):
        if sortie_map and not self.CURRENT_SCREEN.any():
            self.CURRENT_SCREEN = self.update_screen()
        screen = self.CURRENT_SCREEN if self.CURRENT_SCREEN.any() else self.update_screen()
        img_template = cv2.imread(f'assets/{template}.png', 0)
        match = cv2.matchTemplate(screen, img_template, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            if self.DEBUG_MODE:
                if template == '':
                    print(f'<{template}> not found')
                else:
                    print(f'Found <{template}> ({location[0]}, {location[1]})')
            return Dimension(location[0], location[1], mob)
        return None

    @classmethod
    def find_multi(self, template, similarity=SIMILARITY_VALUE, mob=False, siren=False):
        if (mob or siren) and not self.CURRENT_SCREEN.any():
            self.CURRENT_SCREEN = self.update_screen()
        screen = self.CURRENT_SCREEN if self.CURRENT_SCREEN.any() else self.update_screen()
        img_template = cv2.imread(f'assets/{template}.png', 0)
        match = cv2.matchTemplate(screen, img_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(match >= similarity)
        locations = list(zip(locations[1], locations[0]))
        fixed_locs = self.fix_locs([Dimension(x, y, mob, siren) for x, y in locations])
        if fixed_locs:
            return fixed_locs
        return []

    @classmethod
    def tap(self, dimension, delay=1.5):
        Adb.shell(f'input tap {dimension.x} {dimension.y}')
        self.wait(delay)

    @classmethod
    def swipe(self, dimension1, dimension2, duration=250):
        Adb.shell(f'input swipe {dimension1.x} {dimension1.y} {dimension2.x} {dimension2.y} {duration}')

    @classmethod
    def fix_locs(self, locs):
        try:
            fixed_locs = [locs[0]]
            for loc in locs:
                if loc not in fixed_locs:
                    fixed_locs.append(loc)
            return fixed_locs
        except IndexError:
            return []

    @classmethod
    def find_closest(self, coords, coord):
        x, y = coords[spatial.KDTree(coords).query(coord)[1]]
        return Dimension(x, y)

    @classmethod
    def notify(self, msg, title='ajurpy'):
        command = ['notify-send', title, msg]
        subprocess.call(command)

    @classmethod
    def wait(self, duration):
        time.sleep(duration)
    
    @classmethod
    def time_now(self):
        return datetime.now()

    @classmethod
    def time_elapsed(self, end, start):
        hours, remainder = divmod((end-start).seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f'{hours} hours, {minutes} minutes, and {seconds} seconds'

    @classmethod
    def delete_screen(self):
        self.CURRENT_SCREEN = np.array([[]])

Buttons = {
    'battle_start': Dimension(910, 585),
    'auto_battle': Dimension(692, 163),
    'switch_fleet': Dimension(825, 685),
    'evade': Dimension(872, 451),
    'confirm_battle': Dimension(860, 600),
    'strategy_panel': Dimension(865, 504),
    'chapter_prev' : Dimension(43, 497),
    'chapter_next' : Dimension(984, 425),
    'go1': Dimension(759, 487),
    'go2': Dimension(864, 554),
    'confirm': Dimension(525, 486),
    'sort': Dimension(357, 483),
    'back': Dimension(50, 45),
    'sort_by': Dimension(907, 28),
    'time_joined': Dimension(657, 171),
    'index_all': Dimension(280, 220),
    'faction_all': Dimension(280, 335),
    'rarity_all': Dimension(280, 445),
    'rarity_common': Dimension(412, 445),
    'rarity_rare': Dimension(538, 445),
    'disassemble': Dimension(639, 529),
    'home': Dimension(999, 30),
    'battle_home': Dimension(871, 372),
    'hard_mode': Dimension(69, 696),
    'fleet_lock': Dimension(974, 550),
    'dialy': Dimension(661, 682),
    'dialy_70': Dimension(480, 250),
    'dialy_50': Dimension(480, 350),
    'dialy_70_fire': Dimension(480, 250),
    'dialy_70_air': Dimension(480, 350),
    'dialy_50_fire': Dimension(480, 450),
    'dialy_50_air': Dimension(480, 575)
}

MapDetail = {
    # Chapter 1
    '1-1': 1,
    '1-2': 2,
    '1-3': 2,
    '1-4': 3,
    # Chapter 2
    '2-1': 2,
    '2-2': 3,
    '2-3': 3,
    '2-4': 3,
    # Chapter 3
    '3-1': 3,
    '3-2': 3,
    '3-3': 3,
    '3-4': 3,
    # Chapter 4
    '4-1': 3,
    '4-2': 3,
    '4-3': 3,
    '4-4': 4,
    # Chapter 5
    '5-1': 4,
    '5-2': 4,
    '5-3': 4,
    '5-4': 4,
    # Chapter 6
    '6-1': 4,
    '6-2': 4,
    '6-3': 4,
    '6-4': 5,
    # Chapter 7
    '7-1': 5,
    '7-2': 5,
    '7-3': 5,
    '7-4': 5,
    # Chapter 8
    '8-1': 4,
    '8-2': 4,
    '8-3': 4,
    '8-4': 5,
    # Chapter 9
    '9-1': 5,
    '9-2': 5,
    '9-3': 5,
    '9-4': 5,
    # Chapter 10
    '10-1': 6,
    '10-2': 6,
    '10-3': 6,
    '10-4': 6,
    # Chapter 11
    '11-1': 6,
    '11-2': 6,
    '11-3': 6,
    '11-4': 6,
    # Chapter 12
    '12-1': 6,
    '12-2': 6,
    '12-3': 6,
    '12-4': 6,
    # Chapter 13
    '13-1': 6,
    '13-2': 6,
    '13-3': 6,
    '13-4': 7,
    # EVENT ONLY
    # CURRENT EVENT : RYUUJOU
    'c3': 5,
    'd3': 6,
}

# EVENT ONLY
Map = {
    'c3': Dimension(786, 312),
    'd3': Dimension(786, 312),
}
