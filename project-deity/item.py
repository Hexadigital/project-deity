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

import random


# Returns all fields associated with an item instance.
async def get_item(cursor, item_id):
    cursor.execute('''SELECT pi.*, i.description
                      FROM "project-deity".player_items pi
                      INNER JOIN "project-deity".items i ON pi.master_item_id = i.id
                      WHERE pi.id = %s;''',
                   (item_id, ))
    return cursor.fetchone()


# Returns all fields associated with an item instance.
async def get_master_item(cursor, item_id):
    cursor.execute('''SELECT *
                      FROM "project-deity".items
                      WHERE id = %s;''',
                   (item_id, ))
    return cursor.fetchone()


# Creates an item instance and returns the instance ID.
# Returns False if item is a material.
async def create_item_instance(cursor, item_id):
    cursor.execute('''SELECT *
                      FROM "project-deity".items
                      WHERE id = %s;''',
                   (item_id, ))
    master = cursor.fetchone()
    if master["class_type"] == "Material":
        return False
    cursor.execute('''INSERT INTO "project-deity".player_items
                      (name, class_type, image, rarity,
                      modifier, json_attributes, master_item_id)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)
                      RETURNING id;''',
                   (master["name"], master["class_type"], master["image"],
                    master["rarity"], master["modifier"],
                    master["json_attributes"], item_id))
    return cursor.fetchone()["id"]


# Deletes an item instance and returns the success value.
async def delete_item(cursor, item_instance_id):
    cursor.execute('''DELETE FROM "project-deity".player_items
                      WHERE id = %s;''',
                   (item_instance_id, ))
    # TODO: Return False if no such item existed
    return True


# Returns information about an item as a string
async def get_text_description(cursor, item_id):
    item = await get_item(cursor, item_id)
    # Adjust a/an depending on the first letter
    if item["modifier"] is not None:
        first_char = item["modifier"][0].lower()
    else:
        first_char = item["name"][0].lower()
    article = "a"
    if first_char in ["a", "e", "i", "o", "u"]:
        article = "an"

    if item["modifier"] is not None:
        description = "You are looking at %s %s %s."
        return description % (article, item["modifier"], item["name"])
    description = "You are looking at %s %s."
    return description % (article, item["name"])


async def get_container_reward(cursor, item_id):
    cursor.execute('''SELECT cr.*, m.name
                      FROM "project-deity".container_roulette cr
                      LEFT JOIN "project-deity".materials m ON cr.reward_id = m.id
                      WHERE cr.container_id = %s;''',
                   (item_id, ))
    container_chances = cursor.fetchall()
    # TODO: Take player luck into account
    player_chance = random.randint(1, 100)
    for chance in container_chances:
        if player_chance >= chance["min_chance"] and player_chance <= chance["max_chance"]:
            quantity = random.randint(chance["min_quantity"], chance["max_quantity"])
            return (chance["reward_id"], quantity, chance["reward_type"], chance["name"])
    return (None, None, None, None)
