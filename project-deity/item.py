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

import deity
import json
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
async def create_item_instance(cursor, item_id, att_dict={}, modifier_material=None):
    cursor.execute('''SELECT *
                      FROM "project-deity".items
                      WHERE id = %s;''',
                   (item_id, ))
    master = cursor.fetchone()
    # Apply custom attributes if they exist
    json_dict = {}
    if master["json_attributes"] is not None:
        json_dict = json.loads(master["json_attributes"])
    for key in att_dict.keys():
        json_dict[key] = att_dict[key]
    # Apply modifier if it exists
    if modifier_material is None:
        modifier_str = master["modifier"]
    else:
        # Calculate modifier effects
        modifier_dict = json.loads(modifier_material["modifier_json"])
        modifier_str = modifier_dict[master["class_type"]]["Modifier"]
        amount_sign = modifier_dict[master["class_type"]]["Min Amount"][0]
        if "%" in modifier_dict[master["class_type"]]["Min Amount"]:
            percentage = "%"
        else:
            percentage = ""
        min_amount = int(modifier_dict[master["class_type"]]["Min Amount"][1:].replace("%", ""))
        max_amount = int(modifier_dict[master["class_type"]]["Max Amount"][1:].replace("%", ""))
        rand_amount = random.randint(min_amount, max_amount)
        json_dict["Modifier"] = {
            "Material": modifier_material["name"],
            "Amount": amount_sign + str(rand_amount) + percentage,
            "Effects": modifier_dict[master["class_type"]]["Effects"]
        }
    json_str = json.dumps(json_dict, sort_keys=True, indent=4)
    cursor.execute('''INSERT INTO "project-deity".player_items
                      (name, class_type, rarity,
                      modifier, json_attributes, master_item_id)
                      VALUES (%s, %s, %s, %s, %s, %s)
                      RETURNING id;''',
                   (master["name"], master["class_type"], master["rarity"],
                    modifier_str, json_str, item_id))
    instance_id = cursor.fetchone()["id"]
    if modifier_material is None:
        print("Created item instance %s (%s)" % (instance_id, master["name"]))
        return instance_id
    else:
        print("Created item instance %s (%s %s)" % (instance_id, modifier_str, master["name"]))
        return instance_id, modifier_str


# Deletes an item instance and returns the success value.
async def delete_item(cursor, item_instance_id):
    cursor.execute('''DELETE FROM "project-deity".player_items
                      WHERE id = %s;''',
                   (item_instance_id, ))
    # TODO: Return False if no such item existed
    return True


# Returns information about an item as a string
async def get_text_description(cursor, item_instance):
    master_item = await get_item(cursor, item_instance["item_id"])
    if item_instance["modifier"] is not None:
        description = "Name: %s %s\n" % (item_instance["modifier"], master_item["name"])
    else:
        description = "Name: %s\n" % master_item["name"]
    description += "Type: %s\n\n" % master_item["class_type"]
    description += master_item["description"] + "\n\n"
    if item_instance["json_attributes"] is not None:
        json_dict = json.loads(item_instance["json_attributes"])
        if "Base" in json_dict.keys():
            description += "Base Stats: "
            for base_stat in json_dict["Base"].keys():
                description += json_dict["Base"][base_stat] + " " + base_stat + ", "
            description = description[:-2]
        if "Modifier" in json_dict.keys():
            description += "\n" + json_dict["Modifier"]["Material"] + ": "
            description += json_dict["Modifier"]["Amount"] + " " + json_dict["Modifier"]["Effects"]
        if "Crafted By" in json_dict.keys():
            deity_dict = await deity.get_deity_by_id(cursor, json_dict["Crafted By"])
            description += "\nCrafted by %s on %s." % (deity_dict["name"], json_dict["Crafted On"])
    return description.strip()


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
