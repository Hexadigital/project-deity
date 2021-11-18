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

from PIL import Image, ImageDraw
from datetime import datetime


async def get_follower_info(cursor, follower_id):
    cursor.execute('''SELECT f.*, fc.class_name, l.name as current_location_name
                   FROM "project-deity".followers f
                   INNER JOIN "project-deity".follower_classes fc
                   ON f.class_id = fc.id
                   LEFT JOIN "project-deity".locations l
                   ON f.current_location_id = l.id
                   WHERE f.id = %s;''', (follower_id, ))
    return cursor.fetchone()


async def get_follower_info_by_deity(cursor, deity_id):
    cursor.execute('''SELECT f.*, fc.class_name, l.name as current_location_name
                   FROM "project-deity".followers f
                   INNER JOIN "project-deity".follower_classes fc
                   ON f.class_id = fc.id
                   LEFT JOIN "project-deity".locations l
                   ON f.current_location_id = l.id
                   WHERE deity_id = %s;''', (deity_id, ))
    return cursor.fetchone()


async def get_follower_info_by_name(cursor, name):
    cursor.execute('''SELECT f.*, fc.class_name, l.name as current_location_name
                   FROM "project-deity".followers f
                   INNER JOIN "project-deity".follower_classes fc
                   ON f.class_id = fc.id
                   LEFT JOIN "project-deity".locations l
                   ON f.current_location_id = l.id
                   WHERE f.name = %s;''', (name, ))
    return cursor.fetchone()


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
        new_req_exp = await get_exp_requirement(level + 1)
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
        await update_max_health(cursor, follower_id)
        await update_max_mana(cursor, follower_id)
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
    level_up_result = await try_level_up(cursor, follower_id)
    return level_up_result


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
                      WHERE id = %s;''', (follower_info["class_id"], ))
    hp_bonus = cursor.fetchone()["hp_bonus"]
    new_max_health = int((((follower_info["level"] / 2) + follower_info["endurance"]) * 3) + hp_bonus)
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
                      WHERE id = %s;''', (follower_info["class_id"], ))
    mp_bonus = cursor.fetchone()["mp_bonus"]
    new_max_mana = int((((follower_info["level"] / 2) + follower_info["intelligence"]) * 3) + mp_bonus)
    cursor.execute('''UPDATE "project-deity".followers
                      SET mp = %s, max_mp = %s
                      WHERE id = %s;''',
                   (new_max_mana, new_max_mana, follower_id))
    return new_max_mana


# Returns the five starting stat values
async def get_starting_stats(cursor, class_name):
    cursor.execute('''SELECT id, strength, endurance, intelligence, agility, willpower,
                   inv_width, inv_height
                   FROM "project-deity".follower_classes
                   WHERE class_name = %s;''', (class_name, ))
    results = cursor.fetchone()
    return results


# Returns all available avatars
async def get_avatars(cursor, deity_id):
    cursor.execute('''SELECT name, filename
                   FROM "project-deity".avatars
                   WHERE deity_exclusive IS NULL
                   OR deity_exclusive = %s
                   ORDER BY name;''', (deity_id, ))
    results = cursor.fetchall()
    return results


# Changes a follower's title
async def set_title(cursor, follower_id, title):
    cursor.execute('''UPDATE "project-deity".followers
                      SET title = %s
                      WHERE id = %s;''',
                   (title, follower_id))
    return True


# Returns all available titles
async def get_titles(cursor, deity_id):
    cursor.execute('''SELECT title
                   FROM "project-deity".titles
                   WHERE unlocked_for_all
                   ORDER BY title;''')
    # TODO: Have a way to unlock titles (via achievements?)
    results = cursor.fetchall()
    return results


# Changes a follower's avatar
async def set_avatar(cursor, follower_id, filename):
    cursor.execute('''UPDATE "project-deity".followers
                      SET portrait = %s
                      WHERE id = %s;''',
                   (filename, follower_id))
    return True


# Checks if a class is a valid starting class
async def check_starting_class(cursor, class_name):
    cursor.execute('''SELECT tier
                   FROM "project-deity".follower_classes
                   WHERE class_name = %s
                   AND tier = 0;''', (class_name, ))
    results = cursor.fetchone()
    if results is None:
        return False
    return True


async def render_follower_card(cursor, follower_info, double_size=False):
    # Create base layers
    backdrop = Image.open("./images/templates/id.png")
    second_layer = Image.new("RGBA", (240, 160))

    # Apply portrait
    portrait = Image.open("./images/portraits/%s" % follower_info["portrait"])
    second_layer.paste(portrait, (8, 4, 40, 36))

    # Apply name
    name = str(follower_info["name"])
    starting_coords = (44, 5)
    for i in range(0, min(20, len(name))):
        if name[i] != " ":
            num = Image.open("./images/font2/%s.png" % name[i])
            second_layer.paste(num, (starting_coords[0] + (7 * i), starting_coords[1], starting_coords[0] + 7 + (7 * i), starting_coords[1] + 7))

    # Apply class
    class_name = str(follower_info["class_name"])
    starting_coords = (44, 16)
    for i in range(0, min(13, len(class_name))):
        if class_name[i] != " ":
            num = Image.open("./images/font2/%s.png" % class_name[i])
            second_layer.paste(num, (starting_coords[0] + (7 * i), starting_coords[1], starting_coords[0] + 7 + (7 * i), starting_coords[1] + 7))

    # Apply title
    if follower_info["title"] is not None:
        title = str(follower_info["title"])
        starting_coords = (44, 27)
        for i in range(0, min(13, len(title))):
            if title[i] != " ":
                num = Image.open("./images/font2/%s.png" % title[i])
                second_layer.paste(num, (starting_coords[0] + (7 * i), starting_coords[1], starting_coords[0] + 7 + (7 * i), starting_coords[1] + 7))

    # Apply level
    level = str(follower_info["level"])
    starting_coords = (169, 16)
    while len(level) < 3:
        level = "0" + level
    for i in range(0, 3):
        num = Image.open("./images/font1/%s.png" % level[i])
        second_layer.paste(num, (starting_coords[0] + (8 * i), starting_coords[1], starting_coords[0] + 6 + (8 * i), starting_coords[1] + 6))

    # Apply exp
    exp = str(follower_info["exp"])
    starting_coords = (185, 24)
    while len(exp) < 6:
        exp = "0" + exp
    for i in range(0, 6):
        num = Image.open("./images/font1/%s.png" % exp[i])
        second_layer.paste(num, (starting_coords[0] + (8 * i), starting_coords[1], starting_coords[0] + 6 + (8 * i), starting_coords[1] + 6))

    # Apply required exp
    req_exp = str(follower_info["next_level_exp"])
    starting_coords = (185, 32)
    while len(req_exp) < 6:
        req_exp = "0" + req_exp
    for i in range(0, 6):
        num = Image.open("./images/font1/%s.png" % req_exp[i])
        second_layer.paste(num, (starting_coords[0] + (8 * i), starting_coords[1], starting_coords[0] + 6 + (8 * i), starting_coords[1] + 6))

    # Apply luck, reputation, devotion
    starting_coords = (49, 59)
    stat_down = 0
    for stat in ["luck", "reputation", "devotion"]:
        stat_num = str(follower_info[stat])
        while len(stat_num) < 3:
            stat_num = "0" + stat_num
        for i in range(0, 3):
            num = Image.open("./images/font1/%s.png" % stat_num[i])
            second_layer.paste(num, (starting_coords[0] + (8 * i), starting_coords[1] + stat_down, starting_coords[0] + 6 + (8 * i), starting_coords[1] + 6 + stat_down))
        stat_down += 8

    # Apply status points
    stat_points = str(follower_info["stat_points"])
    starting_coords = (121, 110)
    while len(stat_points) < 3:
        stat_points = "0" + stat_points
    for i in range(0, 3):
        num = Image.open("./images/font1/%s.png" % stat_points[i])
        second_layer.paste(num, (starting_coords[0] + (8 * i), starting_coords[1], starting_coords[0] + 6 + (8 * i), starting_coords[1] + 6))

    # Apply stats
    starting_coords = (49, 118)
    stat_down = 0
    for stat in ["strength", "endurance", "intelligence", "agility", "willpower"]:
        stat_num = str(follower_info[stat])
        while len(stat_num) < 3:
            stat_num = "0" + stat_num
        for i in range(0, 3):
            num = Image.open("./images/font1/%s.png" % stat_num[i])
            second_layer.paste(num, (starting_coords[0] + (8 * i), starting_coords[1] + stat_down, starting_coords[0] + 6 + (8 * i), starting_coords[1] + 6 + stat_down))
        stat_down += 8

    # Fill stat bars
    draw = ImageDraw.Draw(second_layer)
    bar_down = 0
    for stat in ["strength", "endurance", "intelligence", "agility", "willpower"]:
        draw.rectangle((79, 119 + bar_down, 79 + (follower_info[stat] - 1), 122 + bar_down), fill='#ffcc00')
        bar_down += 8

    # Draw HP, MP
    hp_length = 79 * (follower_info["hp"] / follower_info["max_hp"])
    draw.rectangle((40, 41, 40 + hp_length, 45), fill='#84d44c')

    mp_length = 79 * (follower_info["mp"] / follower_info["max_mp"])
    draw.rectangle((40, 49, 40 + mp_length, 53), fill='#b0def0')

    # Draw energy
    cursor.execute('''SELECT * FROM "project-deity".daily_login
                   WHERE follower_id = %s;''',
                   (follower_info["id"], ))
    activity = cursor.fetchone()
    last_daily = datetime.date(activity["last_login"])
    todays_date = datetime.date(datetime.now())
    delta = todays_date - last_daily
    if delta.days == 0:
        draw.rectangle((66, 84, 69, 87), fill='#ffcc00')
    if delta.days <= 1:
        draw.rectangle((58, 84, 61, 87), fill='#ffcc00')
    if delta.days <= 2:
        draw.rectangle((50, 84, 53, 87), fill='#ffcc00')

    # Output to file
    final = Image.alpha_composite(backdrop, second_layer)
    if double_size:
        final.resize((480, 320), resample=Image.NEAREST)
    final.save("./images/renders/followers/%s.png" % follower_info["id"])
    return "./images/renders/followers/%s.png" % follower_info["id"]


# Returns follower ID if created, False otherwise
async def create_follower(cursor, name, class_name, deity_id):
    class_info = await get_starting_stats(cursor, class_name)
    # Ensure we got class info
    if class_info is None:
        return False
    cursor.execute('''INSERT INTO "project-deity".followers
                      (name, class_id, deity_id,
                      strength, endurance, intelligence,
                      agility, willpower, inv_width, inv_height)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      RETURNING id;''',
                   (name, class_info["id"], deity_id,
                    class_info["strength"], class_info["endurance"],
                    class_info["intelligence"], class_info["agility"],
                    class_info["willpower"], class_info["inv_width"],
                    class_info["inv_height"]))
    follower_id = cursor.fetchone()["id"]
    await update_max_health(cursor, follower_id)
    await update_max_mana(cursor, follower_id)
    # Create empty equipment record
    cursor.execute('''INSERT INTO "project-deity".follower_equipment
                   (follower_id) VALUES (%s);''',
                   (follower_id, ))
    return follower_id


# Deletes a follower and associated info.
# Returns name, level and class_name.
async def abandon_follower(cursor, follower_id):
    cursor.execute('''SELECT class_id, name, level
                      FROM "project-deity".followers
                      WHERE id = %s;''', (follower_id, ))
    follower_info = cursor.fetchone()
    cursor.execute('''SELECT class_name
                      FROM "project-deity".follower_classes
                      WHERE id = %s;''', (follower_info["class_id"], ))
    class_name = cursor.fetchone()["class_name"]
    # Get list of item instances to delete
    items_to_delete = []
    cursor.execute('''SELECT *
                      FROM "project-deity".follower_equipment
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    equips = cursor.fetchone()
    items_to_delete.append(equips["accessory"])
    items_to_delete.append(equips["helmet"])
    items_to_delete.append(equips["ring"])
    items_to_delete.append(equips["weapon"])
    items_to_delete.append(equips["armor"])
    items_to_delete.append(equips["shield"])
    items_to_delete.append(equips["gloves"])
    items_to_delete.append(equips["legs"])
    items_to_delete.append(equips["boots"])
    cursor.execute('''SELECT slot_num, item_id
                      FROM "project-deity".follower_inventories
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    inv = cursor.fetchall()
    for item in inv:
        items_to_delete.append(item["item_id"])
    # Delete item instances
    for item in items_to_delete:
        if item is None:
            continue
        cursor.execute('''DELETE
                          FROM "project-deity".player_items
                          WHERE id = %s;''',
                       (item, ))
    # Delete equipment record
    cursor.execute('''DELETE
                      FROM "project-deity".follower_equipment
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    # Delete inventory records
    cursor.execute('''DELETE
                      FROM "project-deity".follower_inventories
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    # Delete daily login records
    cursor.execute('''DELETE
                      FROM "project-deity".daily_login
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    # Finally, delete follower record
    cursor.execute('''DELETE
                      FROM "project-deity".followers
                      WHERE id = %s;''',
                   (follower_id, ))
    return follower_info["name"], follower_info["level"], class_name
