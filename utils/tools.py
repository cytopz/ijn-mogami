import time
import subprocess
import cv2
import numpy as np
from scipy import spatial
from utils.adb import Adb

class Dimension:
    def __init__(self, x, y, mob=False):
        self.x = x
        self.y = y
        self.mob = mob
        if mob:
            print("mob, value increased")
            self.inc_val(25)
            self.check_borders()

    def inc_val(self, val):
        self.x += val
        self.y += val

    def dec_val(self, val):
        self.x -= val
        self.y -= val

    def check_borders(self):
        if self.x < 98:
            delta = 98-self.x
            self.x += delta + 6
        if self.y > 651:
            delta = self.y - 651;
            self.y -= delta + 6;
        if self.x > 984:
            if self.y < 169 and self.y > 86:
                delta = 169 - self.y;
                self.y += delta + 25;

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
        res = None
        img_template = cv2.imread('assets/{}.png'.format(template), 0)
        match = cv2.matchTemplate(screen, img_template, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            print(template, location[0], location[1])
            return Dimension(location[0], location[1], mob)
        return None

    @classmethod
    def find_multi(self, template, similarity=SIMILARITY_VALUE, mob=False):
        screen = self.update_screen()
        img_template = cv2.imread('assets/{}.png'.format(template), 0)
        match = cv2.matchTemplate(screen, img_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(match >= similarity)
        fixed_locs = self.fix_locs(list(zip(locations[1], locations[0])))
        if fixed_locs:
            return [Dimension(x, y, mob) for x, y in fixed_locs]
        else:
            return None

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
            idx = 0
            fixed_locs = [locs[0]] 
            for loc in locs:
                if spatial.distance.euclidean(loc, fixed_locs[idx]) > 5 and loc not in fixed_locs:
                    fixed_locs.append(loc)
                    idx += 1
            return fixed_locs
        except IndexError:
            return None

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
