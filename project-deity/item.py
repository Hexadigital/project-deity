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
def get_item(cursor, item_id):
    cursor.execute('''SELECT *
                      FROM player_items
                      WHERE id = %s;''',
                   (item_id, ))
    return cursor.fetchone()


# Creates an item instance and returns the instance ID.
def create_item_instance(cursor, item_id):
    cursor.execute('''SELECT *
                      FROM items
                      WHERE id = %s;''',
                   (item_id, ))
    master = cursor.fetchone()
    cursor.execute('''INSERT INTO player_items
                      (name, class_type, image, value, weight, rarity,
                      modifier, json_attributes)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s);''',
                   (master["name"], master["class_type"], master["image"],
                    master["value"], master["weight"], master["rarity"],
                    master["modifier"], master["json_attributes"]))
    return cursor.fetchone()["id"]
