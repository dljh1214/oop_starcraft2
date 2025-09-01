import heapq
import time
import threading
class Game:
    current_game = None
############-----------------------PROPERTIES----------------###############################
    class PropertyM:
        def __init__(self,object):
            self.object = object
            self.object.property = []
        def tick(self):
            for i in self.object.property:
                i.tick()
    class Properties:
        def __init__(self,object):
            self.object = object
            self.object.property.append(self)
        def tick(self):
            pass
    class LockDown(Properties):
        needed_energy = 100
        stun_tick = 2000
        def __init__(self,object):
            super().__init__(object)
        def lockdown(self,target):
            if self.object.energy > Game.LockDown.needed_energy:
                target.get_stunned(Game.current_game.get_tick()+Game.LockDown.stun_tick)
                self.object.energy-=Game.LockDown.needed_energy
            else:
                print("energy insufficient")
    class SelfRegenerate(Properties):
        health_per_tick = 0.5
        def __init__(self,object):
            super().__init__(object)
        def tick(self):
            if self.object.hp < self.object.max_hp:
                self.object.heal(Game.SelfRegenerate.health_per_tick)
    class SelfRecharge(Properties):
        energy_per_tick = 0.035
        def __init__(self,object):
            super().__init__(object)
        def tick(self):
            self.object.charge(Game.SelfRecharge.energy_per_tick)
    class Cloakable(Properties):
        energy_per_tick = 0.1
        def __init__(self,object):
            super().__init__(object)
            self.object.cloaked = False
        def cloak(self):
            self.object.cloaked = True
        def uncloak(self):
            self.object.cloaked = False
        def tick(self):
            if self.object.cloaked:
                if self.object.energy < Game.Cloakable.energy_per_tick:
                    self.uncloak()
                else:
                    self.object.energy -= Game.Cloakable.energy_per_tick
######-------------UNITS--------############################
    class Unit:
        def __init__(self, hp=100, x=0, y=0,energy=100):
            self.max_hp = hp
            self.hp = hp
            self.coordinate = [x, y]
            self.stunned = False
            self.energy = energy
            Game.current_game.units.append(self)
            self.alive = True
            self.propM = Game.PropertyM(self)
            self.cc = []

        def move(self, x, y):
            if not self.stunned and self.alive:
                self.coordinate = [x, y]
        def attack(self,target):
            if self.stunned or not self.alive:
                print("failed to attack")
                return
            target.get_damage(10)
        def get_damage(self,amount):
            self.hp-=amount
        def heal(self,amount):
            self.hp+=amount
            if self.hp > self.max_hp:
                self.hp = self.max_hp
        def charge(self,amount):
            self.energy+=amount
        def get_stunned(self,end_tick):
            self.stunned = True
            heapq.heappush(self.cc,(end_tick,self.out_stunned))
        def out_stunned(self):
            self.stunned = False
        def tick(self):
            if self.hp <= 0:
                Game.current_game.dead_units.append(self)
                self.alive = False
                return
            if self.cc:
                if self.cc[0][0] <= g.get_tick():
                    _,fn = heapq.heappop(self.cc)
                    fn()
            self.propM.tick()

    class terran_marine(Unit):
        def attack(self,target):
            super().attack(target)
            print('가우스 소총 발사!')

    class zerg_zergling(Unit):
        def __init__(self,hp = 100, x=0,y=0,energy = 100):
            super().__init__(hp,x,y,energy)
            self.regenM = Game.SelfRegenerate(self)
        def attack(self,target):
            super().attack(target)
            print('발톱으로 할퀴기!')

    class protoss_zealot(Unit):
        def attack(self,target):
            super().attack(target)
            print('사이오닉 검으로 공격!')


    class terran_ghost(Unit):
        def __init__(self, hp=100, x=0, y=0, energy=100.0):
            super().__init__(hp, x, y,energy)
            self.cloakM = Game.Cloakable(self)
            self.ldM = Game.LockDown(self)
            self.rcM = Game.SelfRecharge(self)
        def lockdown(self,target):
            self.ldM.lockdown(target)
        def cloak(self):
            self.cloakM.cloak()
        def tick(self):
            super().tick()
    class terran_wraith(Unit):
        def __init__(self, hp=100, x=0, y=0, energy=50.0):
            super().__init__(hp, x, y,energy)
            self.energy = energy
            self.cloakM = Game.Cloakable(self)
        def cloak(self):
            self.cloakM.cloak()
        def uncloak(self):
            self.cloakM.uncloak()

##################################GAME FEATURES#########################################################################
    def __init__(self):
        self.__tick = 0
        self.units = []
        self.dead_units = []
        Game.current_game = self
        self.act_thread = threading.Thread(target = self._get_user_act,daemon = True)
        self.act_thread.daemon = True
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
        for i in self.dead_units:
            self.units.remove(i)
        self.dead_units=[]
        for i in self.units:
            i.tick()
    def game_loop(self):
        self.act_thread.start()
        while True:
            self.__tick += 1
            self.ex_tick()
            time.sleep(1/24)

g = Game()
g.game_loop()
