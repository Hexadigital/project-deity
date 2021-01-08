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

# Finds the first free slot and returns the slot number,
# or returns None if no free slots exist.
async def find_free_slot(cursor, follower_id):
    cursor.execute('''SELECT inv_width, inv_height
                      FROM "project-deity".followers
                      WHERE id = %s;''',
                   (follower_id, ))
    results = cursor.fetchone()
    inv_width = results["inv_width"]
    inv_height = results["inv_height"]
    inv_capacity = inv_width * inv_height
    cursor.execute('''SELECT slot_num
                      FROM "project-deity".follower_inventories
                      WHERE follower_id = %s
                      ORDER BY slot_num ASC;''',
                   (follower_id, ))
    used_slots = [x["slot_num"] for x in cursor.fetchall()]
    for i in range(1, inv_capacity):
        if i not in used_slots:
            return i
    return None


# Returns True if item is added,
# returns False if inventory is full.
async def add_item(cursor, follower_id, item_instance_id):
    item_slot = await find_free_slot(cursor, follower_id)
    if item_slot is None:
        return False
    cursor.execute('''INSERT INTO "project-deity".follower_inventories
                      (follower_id, slot_num, item_id)
                      VALUES (%s, %s, %s);''',
                   (follower_id, item_slot, item_instance_id))
    return True


# Deletes the item in an inventory slot,
# returns deletion status.
async def delete_item(cursor, follower_id, item_id):
    cursor.execute('''DELETE FROM "project-deity".follower_inventories
                      WHERE follower_id = %s
                      AND slot_num = %s;''',
                   (follower_id, item_id))
    # TODO: Return False if slot was already empty
    return True
