from utils.tools import Tools, Dimension

class Sortie:
    def __init__(self):
        self.buttons = {
            'battle_start': Dimension(910, 585),
            'auto_battle': Dimension(692, 163),
            'switch_fleet': Dimension(825, 685),
            'evade': Dimension(872, 451),
            'sort': Dimension(357, 483),
            'tobe_retired_ship': Dimension(100, 109),
            'back': Dimension(50, 45),
            'sort_by': Dimension(907, 28),
            'time_joined': Dimension(657, 141),
            'disassemble': Dimension(639, 529),
            'confirm_battle': Dimension(860, 600),
            'strategy_panel': Dimension(865, 504),
            'go1': Dimension(759, 487),
            'go2': Dimension(864, 554),
            'confirm': Dimension(525, 486)
        }
        self.sortie_map = 't6'
        self.mob_kill_required = 6
        self.kill_count = 0
        self.switch_boss = True
        self.mob_fleet = 2
        self.current_fleet = 1
        self.needstorefocus = False
        self.mob_coords = {}
        self.boss_coord = None
        self.fleet_coord = None
        self.finish = False

    def start(self):
        self.go_to_map()
        self.clear_mob()
        self.kill_boss()

    def go_to_map(self):
        if Tools.find('urgent', 0.725):
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
            if Tools.find('boss', 0.9):
                return
            if Tools.find('urgent', 0.765):
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
        if self.finish:
            print("BOSS IS KILLED ABORT ABORT")
            return
        if Tools.find('urgent', 0.765):
            Tools.tap(self.buttons['confirm'])
        Tools.tap(self.buttons['strategy_panel'])
        if self.switch_boss:
            self.switch_fleet()
        self.fleet_coord = self.get_fleet_coord()
        self.boss_coord = Tools.find('boss', sim)
        while not self.boss_coord:
            self.boss_coord = self.look_around('boss', 1)
        self.watch_for_distraction(self.boss_coord, True)
        if self.finish:
            print("BOSS IS KILLED ABORT ABORT")
            return
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
        self.finish = True
        Tools.wait(7)

    def watch_for_distraction(self, mob_coord, from_boss=False):
        tap_count = 0
        Tools.tap(mob_coord)
        while not Tools.find('battle_start'):
            if Tools.find('cant_reach'):
                mob_coord = self.cant_reach_handler(mob_coord, from_boss)
            if Tools.find('ambush'):
                self.ambush_handler()
            if tap_count == 9:
                mob_coord = self.look_around('boss', 1) if from_boss else self.filter_mob_coords(blacklist=mob_coord)
                if any(self.mob_coords.values()):
                    tap_count = 0
            if tap_count > 15:
                self.mob_coords = self.look_around('mobs', 2, blacklist=mob_coord)
                mob_coord = self.filter_mob_coords()
                tap_count = 0
            if self.finish:
                print("BOSS IS KILLED ABORT ABORT")
                return
            Tools.tap(mob_coord)
            tap_count += 1

    def cant_reach_handler(self, mob_coord, from_boss=False):
        if not from_boss:
            return self.filter_mob_coords(blacklist=mob_coord)
        if self.switch_boss:
            self.switch_fleet()
        self.boss_coord = Tools.find('boss', 0.9)
        if not self.boss_coord:
            self.boss_cord = self.look_around('boss', 1)
        self.mob_coords = self.find_mobs()
        if not any(self.mob_coords.values()):
            self.mob_coords = self.look_around('mobs', 2)
            self.boss_coord = Dimension(512, 360)
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
        Tools.wait(3.5)
        if self.fail_evade():
            Tools.tap(self.buttons['battle_start'])
            if self.is_deck_full():
                self.retire_ship()
                Tools.tap(self.buttons['battle_start'])
            while not Tools.find('touch_to_continue'):
                Tools.wait(20)
            self.end_battle_handler()
            self.mob_kill_required += 1

    def end_battle_handler(self):
        # Tap to continue
        Tools.tap(Dimension(785, 621))
        Tools.tap(Dimension(785, 621))
        # Extra taps incase purple / new ship droped xd
        Tools.tap(Dimension(785, 621))
        Tools.tap(Dimension(785, 621))
        Tools.wait(2)
        # Tap confirm
        Tools.tap(self.buttons['confirm_battle'])  #confirm battle

    def get_fleet_coord(self):
        coord = None
        sim = 0.9
        sim_min = 0.725
        while not coord:
            if sim <= sim_min:
                break
            coord = Tools.find('fleet', sim)
            sim -= 0.05
        if not coord:
            return Dimension(512, 360)
        coord.x += 25
        coord.y += 440
        return coord

    def find_mobs(self):
        self.mob_coords.clear()
        mob_coords = {
            'sirens': [],
            'large': [],
            'medium': [],
            'small': []
        }
        sim = 0.95
        sim_min = 0.625
        coords = []
        for key in mob_coords:
            while sim >= sim_min:
                if key == 'small':
                    sim_min = 0.85
                if key == 'medium':
                    sim_min = 0.7
                if key == 'sirens':
                    if len(mob_coords['sirens']) != 0:
                        break
                    if self.kill_count >= 3:
                        break
                    sim_min = 0.6
                    for i in range(1, 5):
                        coords += Tools.find_multi('siren'+str(i), sim, True, True)
                else:
                    coords = Tools.find_multi('mob_'+key, sim, True)
                if sim <= sim_min:
                    break
                if coords:
                    mob_coords[key] += list(filter(lambda x, k=key: x not in mob_coords[k], coords))
                print(key, ':', mob_coords[key])
                sim -= 0.025
            sim = 0.95
            sim_min = 0.6
        return mob_coords

    def filter_mob_coords(self, blacklist=None, boss_coord=None):
        center_point = None
        mob_coords = []
        if blacklist:
            for key in self.mob_coords:
                print("blacklist : ", self.mob_coords[key])
                if not self.mob_coords[key]:
                    continue
                if blacklist in self.mob_coords[key]:
                    print("remove blacklist")
                    self.mob_coords[key].remove(blacklist)
        if boss_coord:
            center_point = boss_coord
        else:
            center_point = self.get_fleet_coord()
        if not any(self.mob_coords.values()):
            self.mob_coords = self.look_around('mobs', 2)
        for coords in self.mob_coords.values():
            if not coords:
                continue
            for coord in coords:
                x, y = coord.x, coord.y
                mob_coords.append((x, y))
                print(coord)
            if mob_coords:
                break
        if len(mob_coords) == 1:
            return Dimension(mob_coords[0][0], mob_coords[0][1])
        return Tools.find_closest(mob_coords, (center_point.x, center_point.y))

    def look_around(self, what, mode, sim_min=0.8, blacklist=None):
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
                if type(coord) is dict:
                    if blacklist:
                        if blacklist in list(set().union(*coord.values())):
                            continue
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
        Tools.tap(Dimension(639, 606))          # confirm button

    def retire_ship(self):
        Tools.tap(self.buttons['sort'])
        self.sort_time_joined()
        Tools.tap(self.buttons['tobe_retired_ship'])

        # while Tools.find('confirm'):
        #    Tools.tap(Tools.find('confirm'))

        Tools.tap(Dimension(867, 683))       # confirm1
        Tools.tap(Dimension(808, 598))       # confirm2
        Tools.tap(Dimension(635, 481))       # confirm2.5 (>=rare botes)
        # Tap to continue
        Tools.tap(Dimension(785, 621))
        Tools.tap(Dimension(765, 511))       # confirm3
        Tools.tap(self.buttons['disassemble'])       # disassemble
        # Tap to continue
        Tools.tap(Dimension(785, 621))
        Tools.tap(self.buttons['back'])
        Tools.wait(7)
