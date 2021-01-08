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

# Returns all fields associated with an item instance.
async def get_item(cursor, item_id):
    cursor.execute('''SELECT *
                      FROM "project-deity".player_items
                      WHERE id = %s;''',
                   (item_id, ))
    return cursor.fetchone()


# Creates an item instance and returns the instance ID.
async def create_item_instance(cursor, item_id):
    cursor.execute('''SELECT *
                      FROM "project-deity".items
                      WHERE id = %s;''',
                   (item_id, ))
    master = cursor.fetchone()
    cursor.execute('''INSERT INTO "project-deity".player_items
                      (name, class_type, image, value, weight, rarity,
                      modifier, json_attributes)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                      RETURNING id;''',
                   (master["name"], master["class_type"], master["image"],
                    master["value"], master["weight"], master["rarity"],
                    master["modifier"], master["json_attributes"]))
    return cursor.fetchone()["id"]


# Returns information about an item as a string
async def get_text_description(cursor, item_id):
    item = get_item(cursor, item_id)
    if item["modifier"] is not None:
        description = "You are looking at a %s %s. \
                       It has a market value of %s gold, and weighs %s."
        return description % (item["modifier"], item["name"],
                              item["value"], item["weight"])
    description = "You are looking at a %s. \
                   It has a market value of %s gold, and weighs %s."
    return description % (item["name"], item["value"], item["weight"])
