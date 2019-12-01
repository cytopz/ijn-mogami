import time
import subprocess
import cv2
import numpy as np
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
        return f"({self.x}, {self.y})"

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
        if self.y > 651:
            delta = self.y - 651
            self.y -= delta + 6
        if self.x > 984:
            if self.y < 169 and self.y > 86:
                delta = 169 - self.y
                self.y += delta + 25

class Tools:
    SIMILARITY_VALUE = 0.8

    @classmethod
    def update_screen(self, bgr=0): 
        img = None
        while img is None:
            img = cv2.imdecode(np.fromstring(Adb.exec_out('screencap -p'), dtype=np.uint8), bgr)
        return img

    @classmethod
    def find(self, template, similarity=SIMILARITY_VALUE, mob=False):
        screen = self.update_screen()
        img_template = cv2.imread('assets/{}.png'.format(template), 0)
        match = cv2.matchTemplate(screen, img_template, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            print(template, location[0], location[1])
            return Dimension(location[0], location[1], mob)
        return None

    @classmethod
    def find_multi(self, template, similarity=SIMILARITY_VALUE, mob=False, siren=False):
        screen = self.update_screen()
        img_template = cv2.imread('assets/{}.png'.format(template), 0)
        match = cv2.matchTemplate(screen, img_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(match >= similarity)
        locations = list(zip(locations[1], locations[0]))
        fixed_locs = self.fix_locs([Dimension(x, y, mob, siren) for x, y in locations])
        if fixed_locs:
            return fixed_locs
        return []

    @classmethod
    def tap(self, dimension):
        Adb.shell('input tap {} {}'.format(dimension.x, dimension.y))
        time.sleep(1.5)

    @classmethod
    def swipe(self, dimension1, dimension2):
        Adb.shell('input swipe {} {} {} {} 250'.format(dimension1.x, dimension1.y, dimension2.x, dimension2.y))

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
