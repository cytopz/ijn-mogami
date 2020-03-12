from utils.tools import Tools, Dimension, MapDetail, Buttons

class Sortie:
    def __init__(self, sortie_map=None, hard_mode=False, clear_mode=False, kill_req=None):
        self.sortie_map = sortie_map
        self.clear_mode = clear_mode
        self.hard_mode = hard_mode
        self.mob_kill_required = MapDetail[self.sortie_map] if not kill_req else kill_req
        self.kill_count = 0
        self.switch_boss = True
        self.mob_fleet = 1
        self.mob_coords = {}
        self.boss_coord = None
        self.fleet_coord = None
        self.finish = False
        self.is_retire_filtered = False

    def start(self):
        if self.sortie_map:
            self.go_to_map()
        self.clear_mob()
        self.kill_boss()
        self.kill_count = 0
        self.is_retire_filtered = False
        self.finish = False

    def go_to_map(self):
        Tools.tap(Buttons['battle_home'])
        Tools.wait(3)
        if Tools.find('hard_mode') and self.hard_mode:
            Tools.tap(Buttons['hard_mode'])
        elif not Tools.find('hard_mode') and not self.hard_mode:
            Tools.tap(Buttons['hard_mode'])
        if Tools.find('urgent', 0.725):
            Tools.tap(Buttons['confirm'])
        map_loc = Tools.find(self.sortie_map)
        if not map_loc:
            print('Map not found')
            self.go_to_chapter()
            map_loc = Tools.find(self.sortie_map)
        Tools.tap(map_loc)
        Tools.tap(Buttons['go1'])
        if self.is_deck_full():
            self.retire_ship()
            Tools.tap(map_loc)
            Tools.tap(Buttons['go1'])
        Tools.tap(Buttons['go2'])
        print(f'Map {self.sortie_map}, {self.mob_kill_required} mob required to kill')
        Tools.wait(7)
        if Tools.find('fleet_lock'):
            Tools.tap(Buttons['fleet_lock'], 0.5)

    def go_to_chapter(self):
        target_chapter = int(self.sortie_map.split('-')[0])
        current_chapter = 0
        print('Getting current chapter...')
        for chapter in range(1, 13):
            if Tools.find(f'{chapter}-1', sortie_map=True):
                current_chapter = chapter
                break
        Tools.delete_screen()
        if current_chapter != 0:
            print('Current chapter found : ', current_chapter)
            print('Target chapter : ', target_chapter)
            difference = target_chapter - current_chapter
            for _ in range(0, abs(difference)):
                if difference >= 1:
                    print('Selecting next chapter')
                    Tools.tap(Buttons['chapter_next'])
                else:
                    print('Selecting previous chapter')
                    Tools.tap(Buttons['chapter_prev'])
            print('Reached chapter ', target_chapter)

    def clear_mob(self):
        if self.clear_mode:
            return
        if self.mob_fleet > 1:
            self.switch_fleet()
        # to center the view, adjust the values manually
        # Tools.swipe(Dimension(512, 384), Dimension(512, 512))
        while self.kill_count < self.mob_kill_required:
            # Tools.tap(Buttons['strategy_panel'])
            if Tools.find('boss', 0.9):
                return
            if Tools.find('urgent', 0.765):
                Tools.tap(Buttons['confirm'])
            self.fleet_coord = self.get_fleet_coord()
            self.mob_coords = self.find_mobs()
            if not self.mob_coords:
                self.refocus_fleet()
                self.mob_coords = self.look_around('mobs', 2)
            mob_coord = self.filter_mob_coords()
            self.watch_for_distraction(mob_coord)
            self.start_battle()

    def start_battle(self, is_boss=False):
        if self.finish:
            print('BOSS IS KILLED ABORT ABORT')
            return
        # Battle preparation
        print('Battle started')
        Tools.tap(Buttons['battle_start'])
        if self.is_deck_full():
            print('Interrupted, dock full')
            self.retire_ship()
            Tools.tap(Buttons['battle_start'])
            print('Resuming battle')
        # Battle in progress     
        print('Battle in progress...')   
        while not Tools.find('touch_to_continue'):
            # Checking if manual control
            if Tools.find('auto_battle'):
                self.enable_auto()
        # Battle ended
        print('Battle ended')
        self.end_battle_handler()
        print(f'Mob kill count : {self.kill_count}')
        self.finish = is_boss
        Tools.wait(7)

    def kill_boss(self):
        sim = 0.9
        if self.finish:
            print('BOSS IS KILLED ABORT ABORT')
            return
        if Tools.find('urgent', 0.765):
            Tools.tap(Buttons['confirm'])
        # Tools.tap(Buttons['strategy_panel'])
        if self.switch_boss:
            self.switch_fleet()
        self.fleet_coord = self.get_fleet_coord()
        self.boss_coord = Tools.find('boss', sim)
        is_overlap_mob_fleet = True
        while not self.boss_coord:
            self.boss_coord = self.look_around('boss', 1)
            if self.boss_coord:
                break
            if is_overlap_mob_fleet:
                print('Boss might be overlapped with mob fleet. Checking...')
                self.switch_fleet()
                fleet_coord = self.get_fleet_coord()
                if not self.clear_mode:
                    self.mob_coords = self.find_mobs()
                    if not self.mob_coords:
                        self.mob_coords = self.look_around('mob', 2)
                    mob_coord = self.filter_mob_coords()
                    self.watch_for_distraction(mob_coord)
                    Tools.tap(Buttons['back'])
                else:
                    while not self.boss_coord:
                        for direction in ['right', 'down', 'left']:
                            self.boss_coord = self.move_one_tile(fleet_coord, direction)
                            if self.boss_coord:
                                break
                self.switch_fleet()
                self.boss_coord = Tools.find('boss', sim)
                is_overlap_mob_fleet = False
            else:
                print('Boss might be overlapped with boss fleet. Moving boss fleet...')
                self.boss_coord = self.move_one_tile(self.get_fleet_coord(), 'up')
        self.watch_for_distraction(self.boss_coord, from_boss=True)
        if self.finish:
            print('BOSS IS KILLED ABORT ABORT')
            return
        self.start_battle(True)

    def watch_for_distraction(self, mob_coord, from_boss=False):
        tap_count = 0
        while True:
            if Tools.find('cant_reach'):
                mob_coord = self.cant_reach_handler(mob_coord, from_boss)
            if Tools.find('ambush'):
                self.ambush_handler()
            if tap_count == 9:
                mob_coord = (self.look_around('boss', 1) if from_boss 
                            else self.filter_mob_coords(blacklist=mob_coord))
                if any(self.mob_coords.values()):
                    tap_count = 0
            if tap_count > 15:
                self.mob_coords = self.look_around('mobs', 2, blacklist=mob_coord)
                mob_coord = self.filter_mob_coords()
                tap_count = 0
            if self.finish:
                print('BOSS IS KILLED ABORT ABORT')
                return
            if not mob_coord:
                self.mob_coords = self.look_around('mobs', 2) 
                mob_coord = self.filter_mob_coords()
            if Tools.find('battle_start'): 
                print('Entering battle formation')
                return
            print('Attacking ', mob_coord)
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
        self.start_battle()
        self.kill_boss()

    def ambush_handler(self):
        self.evade()
        Tools.wait(3.5)
        if self.fail_evade():
            print('Failed to evade')
            Tools.tap(Buttons['battle_start'])
            if self.is_deck_full():
                self.retire_ship()
                Tools.tap(Buttons['battle_start'])
            # Battle in progress        
            while not Tools.find('touch_to_continue'):
                # Checking if manual control
                if Tools.find('auto_battle'):
                    self.enable_auto()
                Tools.wait(5)
            print('Battle ended')    
            self.end_battle_handler()
            self.mob_kill_required += 1

    def end_battle_handler(self):
        # Tap to continue
        Tools.tap(Dimension(785, 621))
        Tools.tap(Dimension(785, 621))
        if Tools.find('rare'):
            print('new BLUE bote dropped. locking...')
            Tools.tap(Dimension(785, 621))
            Tools.tap(Buttons['confirm'])
        elif Tools.find('elite'):
            print('PURPLE bote dropped')
            Tools.tap(Dimension(785, 621))
            Tools.tap(Buttons['confirm'])
        elif Tools.find('super_rare'):
            print('GOLDEN LEGENDARY bote dropped')
            Tools.tap(Dimension(785, 621))
            Tools.tap(Buttons['confirm'])
        Tools.wait(3)
        # Tap confirm
        Tools.tap(Buttons['confirm_battle'])  #confirm battle
        self.kill_count += 1

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
        coord.y += 120
        return coord

    def find_mobs(self):
        self.mob_coords.clear()
        mob_coords = {
            'large': [],
            'medium': [],
            'small': [],
        }
        sim = 0.95
        sim_min = 0.625
        coords = []
        print('Searching mobs...')
        for key in mob_coords:
            while sim >= sim_min:
                if key == 'small':
                    sim_min = 0.85
                if key == 'medium':
                    sim_min = 0.75
                coords = Tools.find_multi('mob_'+key, sim, True)
                if sim <= sim_min:
                    break
                if coords:
                    mob_coords[key] += list(filter(lambda x, k=key: x not in mob_coords[k], coords))
                sim -= 0.025
            print(f' - {key} : {mob_coords[key]}')
            sim = 0.95
            sim_min = 0.6
        Tools.delete_screen()
        return mob_coords

    def filter_mob_coords(self, blacklist=None, boss_coord=None):
        center_point = None
        mob_coords = []
        if blacklist:
            for key in self.mob_coords:
                print('Blacklist : ', self.mob_coords[key])
                if not self.mob_coords[key]:
                    continue
                if blacklist in self.mob_coords[key]:
                    print('Remove blacklist')
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
                # print(coord)
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
        swipe_directions = ['right', 'down', 'left', 'up']
        for swp in swipe_directions:
            print('Swipe: ', swp)
            if swp == 'right':
                Tools.swipe(mid, Dimension(mid.x + x_dist, mid.y))
            elif swp == 'down':
                Tools.swipe(mid, Dimension(mid.x, mid.y + y_dist))
            elif swp == 'left':
                Tools.swipe(mid, Dimension(mid.x - x_dist, mid.y))
            else:
                Tools.swipe(mid, Dimension(mid.x, mid.y - y_dist))
            while not coord:
                if sim <= sim_min:
                    break
                coord = Tools.find(what, sim) if mode == 1 else self.find_mobs()
                sim -= 0.05
            sim = 0.95
            if coord:
                if isinstance(coord, dict):
                    if blacklist:
                        if blacklist in list(set().union(*coord.values())):
                            continue
                return coord
        return None

    def is_deck_full(self):
        return Tools.find('sort')

    def refocus_fleet(self):
        self.switch_fleet()
        self.switch_fleet()

    def switch_fleet(self):
        Tools.tap(Buttons['switch_fleet'])

    def enable_auto(self):
        print('Enabling auto combat')
        Tools.tap(Dimension(50, 110))

    def evade(self):
        print('Evading ambush')
        Tools.tap(Buttons['evade'])

    def fail_evade(self):
        return Tools.find('battle_start')

    def move_one_tile(self, current_fleet, direction):
        directions = {
            'left': Dimension(current_fleet.x - 100, current_fleet.y),
            'right': Dimension(current_fleet.x + 100, current_fleet.y),
            'up': Dimension(current_fleet.x, current_fleet.y - 100),
            'down': Dimension(current_fleet.x, current_fleet.y + 100)
        }
        Tools.tap(directions[direction])
        return directions[direction]

    def filter_retire_ship(self):
        Tools.tap(Buttons['sort_by'], 1)
        Tools.tap(Buttons['time_joined'], 0.35)
        Tools.tap(Buttons['index_all'], 0.35)
        Tools.tap(Buttons['faction_all'], 0.35)
        Tools.tap(Buttons['rarity_all'], 0.35)
        Tools.tap(Buttons['rarity_common'], 0.35)
        Tools.tap(Buttons['rarity_rare'], 0.35)
        Tools.tap(Dimension(639, 606))          # confirm button
        self.is_retire_filtered = True

    def retire_ship(self):
        print('Retiring ship...')
        Tools.tap(Buttons['sort'], 1.7)
        if not self.is_retire_filtered:
            self.filter_retire_ship()
        # Selecting one row botes
        ship = Dimension(130, 145)
        for _ in range(7):
            Tools.tap(ship, 0.35)
            ship.x += 130
        Tools.wait(0.1)
        Tools.tap(Dimension(867, 683))       # confirm1
        Tools.tap(Dimension(808, 598))       # confirm2
        # Tap to continue
        Tools.tap(Dimension(785, 621))
        Tools.tap(Dimension(765, 511))       # confirm3
        Tools.tap(Buttons['disassemble'])       # disassemble
        # Tap to continue
        Tools.tap(Dimension(785, 621))
        Tools.tap(Buttons['back'])
        Tools.wait(7)
