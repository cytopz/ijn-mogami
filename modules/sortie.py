from utils.tools import Tools, Dimension

class Sortie:
    def __init__(self):
        self.buttons = {
            'battle_start': Dimension(1715, 959),
            'auto_battle': Dimension(1289, 200),
            'switch_fleet': Dimension(1556, 1030),
            'evade': Dimension(1614, 730),
            'sort': Dimension(701, 777),
            'tobe_retired_ship': Dimension(244, 270),
            'back': Dimension(108, 103),
            'sort_by': Dimension(1740, 53),
            'time_joined': Dimension(1257, 145),
            'disassemble': Dimension(1213, 874),
            'confirm_battle': Dimension(1630, 1008),
            'strategy_panel': Dimension(1617, 593),
            'go1': Dimension(1430, 784),
            'go2': Dimension(1627, 915),
            'confirm': Dimension(525, 486)
        }
        self.sortie_map = 'd2'
        self.mob_kill_required = 5
        self.kill_count = 0
        self.switch_boss = True
        self.mob_fleet = 2
        self.current_fleet = 1
        self.needstorefocus = False
        self.mob_coords = {}
        self.boss_coord = None
        self.fleet_coord = None

    def start(self):
        self.go_to_map()
        self.clear_mob()
        self.kill_boss()

    def go_to_map(self):
        if Tools.find('urgent'):
            Tools.tap(self.buttons['confirm'])
        map_loc = Tools.find(self.sortie_map)
        if map_loc:
            Tools.tap(map_loc)
            Tools.tap(self.buttons['go1'])
            if self.is_deck_full():
                self.retire_ship()
                Tools.tap(map_loc)
                Tools.tap(self.buttons['go1'])
            Tools.tap(self.buttons['go2'])
        else:
            print("map not found")
        Tools.wait(7)

    def clear_mob(self):
        if self.mob_fleet > 1:
            self.switch_fleet()
        while self.kill_count < self.mob_kill_required:
            Tools.tap(self.buttons['strategy_panel'])
            if Tools.find('urgent'):
                Tools.tap(self.buttons['confirm'])
            self.fleet_coord = self.get_fleet_coord()
            self.mob_coords = self.find_mobs()
            if not self.fleet_coord:
                self.refocus_fleet()
            if not self.mob_coords:
                self.refocus_fleet()
                self.mob_coords = self.look_around('mobs', 2)
            mob_coord = self.filter_mob_coords()
            self.watch_for_distraction(mob_coord)
            Tools.tap(self.buttons['battle_start'])
            if self.is_deck_full():
                self.retire_ship()
                Tools.tap(self.buttons['battle_start'])
            if not self.is_auto_enabled:
                self.enable_auto()
            while not Tools.find('touch_to_continue'):
                Tools.wait(20)
            self.end_battle_handler()
            self.kill_count += 1
            Tools.wait(7)

    def kill_boss(self):
        sim = 0.9
        if Tools.find('urgent'):
            Tools.tap(self.buttons['confirm'])
        Tools.tap(self.buttons['strategy_panel'])
        if self.switch_boss:
            self.switch_fleet()
        self.fleet_coord = self.get_fleet_coord()
        self.boss_coord = Tools.find('boss', sim)
        while not self.boss_coord:
            self.boss_coord = self.look_around('boss', 1)
        self.watch_for_distraction(self.boss_coord, True)
        Tools.tap(self.buttons['battle_start'])
        if self.is_deck_full():
            self.retire_ship()
            Tools.tap(self.buttons['battle_start'])
        if not self.is_auto_enabled():
            self.enable_auto()
        while not Tools.find('touch_to_continue'):
            Tools.wait(20)
        self.end_battle_handler()
        self.kill_count += 1
        Tools.wait(7)

    def watch_for_distraction(self, mob_coord, from_boss=False):
        tap_count = 0
        Tools.tap(mob_coord)
        while not Tools.find('battle_start'):
            if Tools.find('ambush'):
                self.ambush_handler()
            if Tools.find('cant_reach'):
                mob_coord = self.cant_reach_handler(mob_coord, from_boss)
            if tap_count == 8:
                mob_coord = self.look_around('boss', 1) if from_boss else self.filter_mob_coords(blacklist=mob_coord)
            if tap_count > 15:
                self.mob_coords = self.look_around('mobs', 2)
                mob_coord = self.filter_mob_coords()
                tap_count = 0
            Tools.tap(mob_coord)
            tap_count += 1

    def cant_reach_handler(self, mob_coord, from_boss=False):
        if not from_boss:
            return self.filter_mob_coords(blacklist=mob_coord)
        if self.switch_boss:
            self.switch_fleet()
        self.boss_coord = self.look_around('boss', 1)
        self.mob_coords = self.find_mobs()
        mob_coord = self.filter_mob_coords(boss_coord=self.boss_coord)
        self.watch_for_distraction(mob_coord)
        Tools.tap(self.buttons['battle_start'])
        if self.is_deck_full():
            self.retire_ship()
            Tools.tap(self.buttons['battle_start'])
        if not self.is_auto_enabled():
            self.enable_auto()
        while not Tools.find('touch_to_continue'):
            Tools.wait(20)
        self.end_battle_handler()
        self.kill_count += 1
        Tools.wait(7)
        self.kill_boss()

    def ambush_handler(self):
        self.evade()
        Tools.wait(2)
        if self.fail_evade():
            Tools.tap(self.buttons['battle_start'])
            self.kill_count += 1

    def end_battle_handler(self):
        # Tap to continue
        Tools.tap(Dimension(1328, 621))
        Tools.tap(Dimension(1328, 621))
        # Extra taps incase purple / new ship droped xd
        Tools.tap(Dimension(1328, 621))
        Tools.tap(Dimension(1328, 621))
        Tools.wait(2)
        # Tap confirm
        Tools.tap(self.buttons['confirm_battle'])  #confirm battle

    def get_fleet_coord(self):
        coord = None
        sim = 0.9
        sim_min = 0.65
        while not coord:
            if sim <= sim_min:
                break
            coord = Tools.find('fleet', sim)
            sim -= 0.05
        coord.x += 25
        coord.y += 160
        return coord

    def find_mobs(self):
        self.mob_coords.clear()
        mob_coords = {
            'large': [],
            'medium': [],
            'small': []
        }
        sim = 0.95
        sim_min = 0.575
        for key in mob_coords:
            while not mob_coords[key]:
                if key == 'small':
                    sim_min = 0.825
                if key == 'medium':
                    sim_min = 0.7
                if sim <= sim_min:
                    break
                mob_coords[key] = Tools.find_multi('mob_'+key, sim, True)
                print(key, ':', mob_coords[key])
                sim -= 0.025
            sim = 0.95
            sim_min = 0.6
        return mob_coords

    def filter_mob_coords(self, blacklist=None, boss_coord=None):
        center_point = None
        mob_coords = []
        if blacklist:
            for coords in self.mob_coords.values():
                print("blacklist : ", coords)
                if not coords:
                    continue
                if blacklist in coords:
                    coords.remove(blacklist)
        if boss_coord:
            center_point = boss_coord
        else:
            center_point = self.get_fleet_coord()
        for coords in self.mob_coords.values():
            if not coords:
                continue
            for coord in coords:
                x, y = coord.x, coord.y
                mob_coords.append((x, y))
                print(x, y)
            if mob_coords:
                break
        if len(mob_coords) == 1:
            return Dimension(mob_coords[0][0], mob_coords[0][1])
        return Tools.find_closest(mob_coords, (center_point.x, center_point.y))

    def look_around(self, what, mode, sim_min=0.8):
        coord = None
        sim = 0.95
        mid = Dimension(512, 384)
        x_dist = 2100
        y_dist = 1100
        swipe_directions = ['r', 'd', 'l', 'u']
        for swp in swipe_directions:
            if swp == 'r':
                Tools.swipe(mid, Dimension(mid.x + x_dist, mid.y))
            elif swp == 'd':
                Tools.swipe(mid, Dimension(mid.x, mid.y + y_dist))
            elif swp == 'l':
                Tools.swipe(mid, Dimension(mid.x - x_dist, mid.y))
            else:
                Tools.swipe(mid, Dimension(mid.x, mid.y - y_dist))
            while not coord:
                print("swipe: ", swp)
                if sim <= sim_min:
                    break
                coord = Tools.find(what, sim) if mode == 1 else self.find_mobs()
                sim -= 0.05
            sim = 0.95
            if coord:
                return coord
        return None

    def is_deck_full(self):
        return Tools.find('sort', 0.7)

    def is_auto_enabled(self):
        return not Tools.find('auto', 0.8)

    def refocus_fleet(self):
        self.switch_fleet()
        self.switch_fleet()

    def switch_fleet(self):
        Tools.tap(self.buttons['switch_fleet'])

    def enable_auto(self):
        Tools.tap(self.buttons['auto_battle'])

    def evade(self):
        Tools.tap(self.buttons['evade'])

    def fail_evade(self):
        return Tools.find('battle_start')

    def sort_time_joined(self):
        Tools.tap(self.buttons['sort_by'])
        Tools.tap(self.buttons['time_joined'])
        Tools.tap(Dimension(1197, 1017))          # confirm button

    def retire_ship(self):
        Tools.tap(self.buttons['sort'])
        self.sort_time_joined()
        Tools.tap(self.buttons['tobe_retired_ship'])

        # while Tools.find('confirm'):
        #    Tools.tap(Tools.find('confirm'))

        Tools.tap(Dimension(1621, 1017))       # confirm1
        Tools.tap(Dimension(1532, 981))       # confirm2
        Tools.tap(Dimension(1188, 774))       # confirm2.5 (>=rare botes)
        # Tap to continue
        Tools.tap(Dimension(1328, 621))
        Tools.tap(Dimension(1447, 818))       # confirm3
        Tools.tap(self.buttons['disassemble'])       # disassemble
        # Tap to continue
        Tools.tap(Dimension(1328, 621))
        Tools.tap(self.buttons['back'])
        Tools.wait(3)
