from abc import abstractmethod
from collections import deque
import time
import threading
class game:
    current_game = None
    class propertyM:
        def __init__(self,object):
            self.object = object
            self.object.properties = []
        def tick(self):
            for i in self.object.properties:
                i.tick()
    class properties:
        def __init__(self,object):
            self.object = object
            self.object.properties.append(self)
    class self_regenerate(properties):
        health_per_tick = 10
        def __init__(self,object):
            super().__init__(object)
        def tick(self):
            self.object.hp+=game.self_regenerate.health_per_tick
    class cloakable(properties):
        energy_per_tick = 5
        def __init__(self,object):
            super().__init__(object)
            object.cloaked = False
        def cloak(self):
            self.object.cloaked = True
        def uncloak(self):
            self.object.cloaked = False
        def tick(self):
            if self.object.cloaked == True:
                self.object.energy-=game.cloakable.energy_per_tick
                if self.object.energy < game.cloakable.energy_per_tick:
                    self.uncloak()
    class Unit:
        def __init__(self, hp=100, x=0, y=0):
            self.hp = hp
            self.coordinate = [x, y]
            self.stunned = False
            game.current_game.units.append(self)
            self.propM = game.propertyM(self)

        def move(self, x, y):
            if not self.stunned:
                self.coordinate = [x, y]

        @abstractmethod
        def attack(self):
            pass

        def tick(self):
            self.propM.tick()

    class terran_marine(Unit):
        def attack(self):
            if not self.stunned:
                print('가우스 소총 발사!')
        def tick(self):
            pass

    class zerg_zergling(Unit):
        def __init__(self,hp = 100, x=0,y=0):
            super().__init__(hp,x,y)
            self.regenM = game.self_regenerate(self)
        def attack(self):
            if not self.stunned:
                print('발톱으로 할퀴기!')

    class protoss_zealot(Unit):
        def attack(self):
            if not self.stunned:
                print('사이오닉 검으로 공격!')


    class terran_ghost(Unit):
        stun_time = 131
        needed_energy = 100.0

        def __init__(self, hp=100, x=0, y=0, energy=50.0):
            super().__init__(hp, x, y)
            self.energy = energy
            self.begin_tick = deque([])
            self.cloakM = game.cloakable(self)

        def lockdown(self, target):
            if self.energy > game.terran_ghost.needed_energy:
                target.stunned = True
                self.begin_tick.append((game.current_game.get_tick(),target))
        def cloak(self):
            self.cloakM.cloak()
        def tick(self):
            if self.begin_tick:
                if game.current_game.get_tick() - self.begin_tick[0][0] >= game.terran_ghost.stun_time:
                    _,target = self.begin_tick.popleft()
                    if target in game.current_game.units:
                        target.stunned = False
            self.energy+=0.035
            self.propM.tick()
    class terran_wraith(Unit):
        def __init__(self, hp=100, x=0, y=0, energy=50.0):
            super().__init__(hp, x, y)
            self.energy = energy
            self.cloakM = game.cloakable(self)
        def cloak(self):
            self.cloakM.cloak()
        def tick(self):
            self.propM.tick()

    def __init__(self):
        self.__tick = 0
        self.units = []
        game.current_game = self
        self.act_thread = threading.Thread(target = self._get_user_act,daemon = True)
    def _get_user_act(self):
        while True:
            act = input()
            if act:
                try:
                    exec(act)
                except:
                    print("wrong argument")
    def get_tick(self):
        return self.__tick
    def ex_tick(self):
        for i in self.units:
            i.tick()
    def game_loop(self):
        self.act_thread.start()
        while True:
            self.__tick += 1
            self.ex_tick()
            time.sleep(1/24)

g = game()
g.game_loop()