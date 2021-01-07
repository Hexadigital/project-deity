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

'''# Returns False if the player cannot level up,
# otherwise returns their new level.
def try_level_up(self):
    if self.exp >= self.exp_req:
        self.exp -= self.exp_req
        self.level += 1
        self.update_exp_requirement()
        # Update stats and heal
        self.update_max_health()
        self.update_max_mana()
        self.hp = self.maxhp
        self.mp = self.maxmp
        return self.level
    else:
        return False

# Calculates the required experience for the next level.
# This formula was used in my first MMO, Restructured.
# Might need to adjust it later.
def update_exp_requirement(self):
    exp_formula1 = (self.level + 1) ^ 3
    exp_formula2 = 6 * (self.level + 1) ^ 2
    exp_formula3 = 17 * (self.level + 1) - 12
    self.exp_req = (50 / 3) * (exp_formula1 - exp_formula2 + exp_formula3)

# Adds the given amount of experience and tries to level up.
def add_exp(self, amount):
    self.exp += amount
    return self.try_level_up()

# Adds the given amount of currency.
def add_income(self, amount):
    self.monies += amount'''


# Resets the max health based off new level/stats.
async def update_max_health(cursor, follower_id):
    cursor.execute('''SELECT class_id, level, endurance
                      FROM followers
                      WHERE id = %s;''', (follower_id, ))
    follower_info = cursor.fetchone()
    cursor.execute('''SELECT hp_bonus
                      FROM follower_classes
                      WHERE id = %s;''', (follower_info[0]))
    hp_bonus = cursor.fetchone()[0]
    new_max_health = int((((follower_info[1] / 2) + follower_info[2]) * 3)
                         + hp_bonus)
    cursor.execute('''UPDATE followers
                      SET hp = %s, max_hp = %s
                      WHERE id = %s''',
                   (new_max_health, new_max_health, follower_id))
    return new_max_health


# Resets the max mana based off new level/stats.
async def update_max_mana(cursor, follower_id):
    cursor.execute('''SELECT class_id, level, intelligence
                      FROM followers
                      WHERE id = %s;''', (follower_id, ))
    follower_info = cursor.fetchone()
    cursor.execute('''SELECT mp_bonus
                      FROM follower_classes
                      WHERE id = %s;''', (follower_info[0]))
    mp_bonus = cursor.fetchone()[0]
    new_max_mana = int((((follower_info[1] / 2) + follower_info[2]) * 3)
                       + mp_bonus)
    cursor.execute('''UPDATE followers
                      SET mp = %s, max_mp = %s
                      WHERE id = %s''',
                   (new_max_mana, new_max_mana, follower_id))
    return new_max_mana


# Returns the five starting stat values
async def get_starting_stats(cursor, class_name):
    cursor.execute('''SELECT strength, endurance, intelligence, agility, willpower
                   FROM follower_classes
                   WHERE class_name = %s;''', (class_name, ))
    results = cursor.fetchone()
    return results
