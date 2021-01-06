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
        # Assign starting stats
        starting_stats = get_starting_stats(class_name)
        self.strength = starting_stats[0]
        self.endurance = starting_stats[1]
        self.intelligence = starting_stats[2]
        self.agility = starting_stats[3]
        self.willpower = starting_stats[4]
        self.luck = 3
        # Stat points to allocate
        self.stat_points = 0
        self.reputation = 0
        self.devotion = 0
        self.maxhp = 0  # TODO
        # Current health
        self.hp = 0  # TODO
        self.maxmp = 0  # TODO
        # Current mana
        self.mp = 0  # TODO
        self.equipment = None  # TODO
        self.inventory = None  # TODO

    def try_level_up(self):
        return None  # TODO

    # Adds the given amount of experience and tries to level up.
    def add_exp(self, amount):
        self.exp += amount
        return self.try_level_up()

    # Adds the given amount of currency.
    def add_income(self, amount):
        self.monies += amount


def get_starting_stats(class_name):
    starting_stats = {
        "Alchemist": [0, 1, 4, 3, 3],
        "Brawler": [3, 4, 1, 2, 1],
        "Craftsman": [2, 2, 3, 2, 2],
        "Elementalist": [1, 2, 3, 2, 3],
        "Merchant": [1, 1, 2, 1, 1],
        "Necromancer": [1, 1, 4, 2, 3],
        "Ranger": [2, 1, 3, 4, 1],
        "Rogue": [1, 1, 2, 4, 3],
        "Soldier": [4, 3, 1, 1, 2]
    }
    return starting_stats[class_name]
