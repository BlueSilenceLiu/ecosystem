from typing import *
from random import randint as ri, choice as cc, random as rd
from matplotlib import pyplot as plt
import time as t
import os
import numpy as np

# grass
gras_grow_time = 12
gras_mass = 5
# herbivore
herb_initial_satiety = 10
herb_starve_death_satiety = -10
herb_energy_consume = 1     # per turn
herb_marriage_satiety = 12
herb_give_birth_satiety = 10
herb_pregnancy_time = 6
herb_pregnancy_probability = 0.6
herb_birth_probability = 0.95
herb_mass = 50
herb_lifespan = 100
herb_lifespan_sigma = 3
# carnivore
carn_initial_satiety = 50
carn_starve_death_satiety = -30
carn_predation_success_rate = 0.2
carn_energy_consume = 5
carn_marriage_satiety = 60
carn_give_birth_satiety = 50
carn_pregnancy_time = 8
carn_pregnancy_probability = 0.4
carn_birth_probability = 0.95
carn_lifespan = 100
carn_lifespan_sigma = 3
# logging
log_file_path = "detail.log"

logfile = open(log_file_path, mode='a')
def _log(string):
    logfile.write(string+"\n")

class Creature:
    def next(self):
        pass


class Grass(Creature):
    all_gras = []  # type: List[Grass]

    def __init__(self):
        self.covered = True
        self.grow_timer = 0

        self.all_gras.append(self)
        self._id = len(self.all_gras) - 1

    def be_eaten(self):
        self.covered = False
        self.grow_timer = gras_grow_time

    def next(self):
        if self.grow_timer > 0:
            self.grow_timer -= 1
            if self.grow_timer == 0:
                self.covered = True


class Herbivore(Creature):
    all_herb = []  # type: List[Union[Herbivore, None]]

    def __init__(self):
        self.satiety = herb_initial_satiety
        self.children = []
        self.gender = ri(0, 1)  # 0: female; 1: male
        self.mate = None
        self.age = 0
        self.lifespan = abs(int(np.random.normal(loc=herb_lifespan,
                                                 scale=herb_lifespan_sigma,
                                                 size=(1, 1))[0]))

        self.pregnant = False
        self.pregnant_timer = self.gender

        self.all_herb.append(self)
        self._id = len(self.all_herb) - 1

    def be_eaten(self):
        self.kill()

    def starve_to_death(self):
        _log(f"(herb) {self._id} starves to death.")
        self.kill()

    def old_age(self):
        _log(f"(herb) {self._id} died of old age, at {self.age} months")
        self.kill()

    def kill(self):
        self.all_herb[self._id] = None
        if self.mate is not None:
            self.mate.mate = None
        del self

    def give_birth(self):
        child = Herbivore()
        self.children.append(child)
        if self.mate is None:
            _log(f"(herb) {self._id} had a child {child._id}, whose father had been dead.")
        else:
            self.mate.children.append(child)
            _log(f"(herb) {self._id} & {self.mate._id} had a child {child._id}.")

    def next(self):
        self.age += 1
        if self.age == self.lifespan:
            self.old_age()
        self.satiety -= herb_energy_consume
        # random eating system
        if ri(0, herb_initial_satiety) < herb_initial_satiety - self.satiety:
            for i in Grass.all_gras:
                if i.covered:
                    i.be_eaten()
                    self.satiety += gras_mass
                    break
        # starve to death
        if self.satiety <= herb_starve_death_satiety:
            self.starve_to_death()
        # marriage
        if self.satiety >= herb_marriage_satiety:
            for i in self.all_herb:
                if i is not None:
                    if self.mate is None:
                        if i.gender != self.gender:
                            if i.satiety >= herb_marriage_satiety:
                                self.mate = i
                                i.mate = self
                                _log(f"marriage: (herb) {self._id} & {self.mate._id}")
                                break
        # give birth
        if self.mate is not None:
            if self.satiety >= herb_give_birth_satiety:
                if self.mate.satiety >= herb_give_birth_satiety:  # consider birth probability
                    if rd() < herb_pregnancy_probability:
                        if self.mate == 0:
                            female = self
                        else:
                            female = self.mate
                        female.pregnant_timer = herb_pregnancy_time
                        female.pregnant = True
                        _log(f"(herb) {female._id} got pregnant.")
        if self.gender == 0:
            self.pregnant_timer -= 1
        if self.pregnant_timer == 0:
            if rd() < herb_birth_probability:
                self.give_birth()
            else:
                _log(f"(herb) {self._id} had a miscarriage.")
            self.pregnant = False
        # TODO: Humanized Animals:
        #  a) raise children
        #  b) feed parents
        #  c) couple care


class Carnivore(Creature):
    all_carn = []  # type: List[Union[Carnivore, None]]

    def __init__(self):
        self.satiety = carn_initial_satiety
        self.children = []
        self.gender = ri(0, 1)
        self.mate = None
        self.age = 1
        self.lifespan = abs(int(np.random.normal(loc=carn_lifespan,
                                                 scale=carn_lifespan_sigma,
                                                 size=(1, 1))[0]))

        self.pregnant = False
        self.pregnant_timer = self.gender

        self.all_carn.append(self)
        self._id = len(self.all_carn) - 1

    def starve_to_death(self):
        _log(f"(carn) {self._id} starves to death.")
        self.kill()

    def old_age(self):
        _log(f"(carn) {self._id} died of old age, at {self.age} months")
        self.kill()

    def kill(self):
        self.all_carn[self._id] = None
        if self.mate is not None:
            self.mate.mate = None
        del self

    def give_birth(self):
        child = Carnivore()
        self.children.append(child)
        if self.mate is None:
            _log(f"(carn) {self._id} had a child {child._id}, whose father had been dead.")
        else:
            self.mate.children.append(child)
            _log(f"(carn) {self._id} & {self.mate._id} had a child {child._id}.")

    def next(self):
        self.age += 1
        if self.age == self.lifespan:
            self.old_age()
        self.satiety -= carn_energy_consume
        # eating
        if ri(0, carn_initial_satiety) < carn_initial_satiety - self.satiety:
            if rd() < carn_predation_success_rate:
                available = [i for i in Herbivore.all_herb if i is not None]
                try:
                    victim = cc(available)
                except IndexError:
                    pass
                else:
                    _log(f"(herb) {victim._id} was eaten up by (carn) {self._id}")
                    self.satiety += herb_mass + victim.satiety
                    victim.be_eaten()
        # starve to death
        if self.satiety <= carn_starve_death_satiety:
            self.starve_to_death()
        # marriage
        if self.satiety >= carn_marriage_satiety:
            if self.mate is None:
                for i in self.all_carn:
                    if i is not None:
                        if i.gender != self.gender:
                            if i.satiety >= carn_marriage_satiety:
                                self.mate = i
                                i.mate = self
                                _log(f"marriage: (carn) {self._id} & {self.mate._id}")
                                break
        # give birth
        if self.mate is not None:
            if self.satiety >= carn_give_birth_satiety:
                if self.mate.satiety >= carn_give_birth_satiety:  # consider birth probability
                    if rd() < carn_pregnancy_probability:
                        if self.mate == 0:
                            female = self
                        else:
                            female = self.mate
                        if female.pregnant:
                            pass
                        else:
                            female.pregnant_timer = carn_pregnancy_time
                            female.pregnant = True
                            _log(f"(carn) {female._id} got pregnant.")
        if self.gender == 0:
            self.pregnant_timer -= 1
        if self.pregnant_timer == 0:
            if rd() < carn_birth_probability:
                self.give_birth()
            else:
                _log(f"(carn) {self._id} had a miscarriage.")
            self.pregnant = False


if __name__ == '__main__':
    origin_size = os.path.getsize(log_file_path)
    _log("************ start ************")
    gras_num = int(input("gras:"))
    herb_num = int(input("herb:"))
    carn_num = int(input("carn:"))
    _log(f"id = {hex(t.time_ns())[2:]}")
    _log("details:")
    creatures = [Herbivore() for _ in range(herb_num)] + \
                [Carnivore() for _ in range(carn_num)] + \
                [Grass() for _ in range(gras_num)]  # type: List[Creature]
    max_turn = int(input("max time(month)\n(0 for forever, until no herb or carn exist):"))
    turn = 0
    g = []
    h = []
    c = []
    while True:
        turn += 1
        _log(f"\n\n------------------turn: {turn}")
        _log("Events:")
        for i in Carnivore.all_carn + Herbivore.all_herb + Grass.all_gras:
            if i is not None:
                i.next()
        print(f"year {int(turn / 12) + 1}, month {turn % 12 + 1}: over.")
        g.append(len([0 for i in Grass.all_gras if i.covered]))
        h.append(len([0 for i in Herbivore.all_herb if i is not None]))
        c.append(len([0 for i in Carnivore.all_carn if i is not None]))
        # print(f"g:{len([0 for i in Grass.all_gras if i.covered])}/{len(Grass.all_gras)}")
        # print(f"h:{len([0 for i in Herbivore.all_herb if i is not None])}")
        # print(f"c:{len([0 for i in Carnivore.all_carn if i is not None])}")
        _log(f"\nTotal: \ng: {g[-1]}\nh: {h[-1]}\nc: {c[-1]}")
        if max_turn == 0 and h[-1] == 0 and c[-1] == 0:
            break
        elif turn == max_turn:
            break

    _log("************  end  ************\n\n\n")

    logfile.close()
    end_size = os.path.getsize(log_file_path)

    size = end_size - origin_size
    size_units = ["B", "KB", "MB", "GB", "TB"]
    unit = "B"
    for i in range(len(size_units)-1):
        if size >= 512:
            size = int(size/1024*100)/100
            unit = size_units[i+1]
    print(f"log space taken: {size}{unit}")

    plt.plot(g, label="grass", color="green")
    plt.plot(h, label="herbivore")
    plt.plot(c, label="carnivore")
    plt.legend()
    plt.show()
