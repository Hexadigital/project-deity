# This file is part of Project Deity.
# Copyright 2020-2021, Frostflake (L.A.)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

class Follower(object):
    def __init__(self, id_num, name, class_name, gender, deity):
        # Internal ID
        self.id = id_num
        self.name = name
        self.class_name = class_name
        self.gender = gender
        self.deity = deity
        self.level = 1
        self.exp = 0
        self.monies = 100
        self.strength = 0  # TODO
        self.endurance = 0  # TODO
        self.intelligence = 0  # TODO
        self.agility = 0  # TODO
        self.willpower = 0  # TODO
        self.luck = 3
        self.reputation = 0
        self.devotion = 0
        self.maxhp = 0  # TODO
        self.hp = 0  # TODO
        self.maxmp = 0  # TODO
        self.mp = 0  # TODO
        self.equipment = None  # TODO
        self.inventory = None  # TODO

    def try_level_up(self):
        return None  # TODO

    def gain_exp(self, exp):
        self.exp += exp
        return self.try_level_up()
