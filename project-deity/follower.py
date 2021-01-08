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

# Returns True if the player can level up
# Returns False otherwise
async def try_level_up(cursor, follower_id):
    cursor.execute('''SELECT exp, next_level_exp, level, stat_points
                      FROM "project-deity".followers
                      WHERE id = %s;''', (follower_id, ))
    result_dict = cursor.fetchone()
    current_exp = result_dict["exp"]
    req_exp = result_dict["next_level_exp"]
    level = result_dict["level"]
    stat_points = result_dict["stat_points"]
    if current_exp >= req_exp:
        # Get exp requirement for next level
        new_req_exp = get_exp_requirement(level + 1)
        stat_points += 3
        # Update follower records
        cursor.execute('''UPDATE "project-deity".followers
                      SET exp = %s, level = %s,
                      next_level_exp = %s, stat_points = %s
                      WHERE id = %s;''',
                       (current_exp - req_exp,
                        level + 1, new_req_exp,
                        stat_points, follower_id))
        # Update health and mana, and heal
        update_max_health(cursor, follower_id)
        update_max_mana(cursor, follower_id)
        return True
    else:
        return False


# Calculates the required experience for the next level.
# This formula was used in my first MMO, Restructured.
# Might need to adjust it later.
async def get_exp_requirement(level):
    exp_formula1 = (level + 1) ^ 3
    exp_formula2 = 6 * (level + 1) ^ 2
    exp_formula3 = 17 * (level + 1) - 12
    return (50 / 3) * (exp_formula1 - exp_formula2 + exp_formula3)


# Adds the given amount of exp, returns True if follower leveled up.
async def add_exp(cursor, follower_id, amount):
    cursor.execute('''SELECT exp
                      FROM "project-deity".followers
                      WHERE id = %s;''', (follower_id, ))
    current_exp = cursor.fetchone()["exp"]
    new_exp = current_exp + amount
    cursor.execute('''UPDATE "project-deity".followers
                      SET exp = %s
                      WHERE id = %s;''',
                   (new_exp, follower_id))
    return try_level_up(follower_id)


# Adds the given amount of currency.
async def add_monies(cursor, follower_id, amount):
    cursor.execute('''SELECT monies
                      FROM "project-deity".followers
                      WHERE id = %s;''', (follower_id, ))
    current_monies = cursor.fetchone()["monies"]
    new_monies = current_monies + amount
    cursor.execute('''UPDATE "project-deity".followers
                      SET monies = %s
                      WHERE id = %s;''',
                   (new_monies, follower_id))
    return new_monies


# Resets the max health based off new level/stats.
async def update_max_health(cursor, follower_id):
    cursor.execute('''SELECT class_id, level, endurance
                      FROM "project-deity".followers
                      WHERE id = %s;''', (follower_id, ))
    follower_info = cursor.fetchone()
    cursor.execute('''SELECT hp_bonus
                      FROM "project-deity".follower_classes
                      WHERE id = %s;''', (follower_info["class_id"]))
    hp_bonus = cursor.fetchone()["hp_bonus"]
    new_max_health = int((((follower_info["level"] / 2)
                           + follower_info["endurance"]) * 3) + hp_bonus)
    cursor.execute('''UPDATE "project-deity".followers
                      SET hp = %s, max_hp = %s
                      WHERE id = %s''',
                   (new_max_health, new_max_health, follower_id))
    return new_max_health


# Resets the max mana based off new level/stats.
async def update_max_mana(cursor, follower_id):
    cursor.execute('''SELECT class_id, level, intelligence
                      FROM "project-deity".followers
                      WHERE id = %s;''', (follower_id, ))
    follower_info = cursor.fetchone()
    cursor.execute('''SELECT mp_bonus
                      FROM "project-deity".follower_classes
                      WHERE id = %s;''', (follower_info["class_id"]))
    mp_bonus = cursor.fetchone()["mp_bonus"]
    new_max_mana = int((((follower_info["level"] / 2)
                         + follower_info["intelligence"]) * 3) + mp_bonus)
    cursor.execute('''UPDATE "project-deity".followers
                      SET mp = %s, max_mp = %s
                      WHERE id = %s;''',
                   (new_max_mana, new_max_mana, follower_id))
    return new_max_mana


# Returns the five starting stat values
async def get_starting_stats(cursor, class_name):
    cursor.execute('''SELECT strength, endurance, intelligence, agility, willpower
                   FROM "project-deity".follower_classes
                   WHERE class_name = %s;''', (class_name, ))
    results = cursor.fetchone()["class_name"]
    return results
