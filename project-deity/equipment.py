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

equippable_item_types = ["Accessory", "Helmet", "Ring", "Weapon", "Armor",
                         "Shield", "Gloves", "Legs", "Boots"]


# Returns False if nothing was done
# Returns True if item was equipped to an empty slot successfully
# Returns the item ID of the previously equipped item otherwise
async def equip_item(cursor, follower_id, slot_num):
    # What inventory item are we equipping?
    cursor.execute('''SELECT item_id
                      FROM "project-deity".follower_inventories
                      WHERE follower_id = %s
                      AND slot_num = %s;''',
                   (follower_id, slot_num))
    item_id = cursor.fetchone()["item_id"]
    # What class is the item?
    cursor.execute('''SELECT class_type
                      FROM "project-deity".player_items
                      WHERE id = %s;''',
                   (item_id, ))
    class_type = cursor.fetchone()["class_type"]
    # Is this a piece of equipment?
    if class_type not in equippable_item_types:
        return False
    # Is there an item equipped in this slot?
    cursor.execute('''SELECT *
                      FROM "project-deity".follower_equipment
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    old_item = cursor.fetchone()[class_type.lower()]
    # Handle inventory management
    if old_item is not None:
        # Return item to inventory. We can reuse the
        # equipping item's slot so we don't need to
        # worry about inventory space.
        cursor.execute('''UPDATE "project-deity".follower_inventories
                          SET item_id = %s
                          WHERE follower_id = %s
                          AND slot_num = %s;''',
                       (item_id, follower_id, slot_num))
    else:
        # If we aren't reusing the inventory slot, then
        # we need to remove the item we're equipping
        # from the inventory.
        cursor.execute('''DELETE FROM "project-deity".follower_inventories
                          WHERE follower_id = %s
                          AND slot_num = %s;''',
                       (follower_id, slot_num))
    # Equip new item
    # Yes, yes, string concatination for SQL is a sin
    # but in this case it's not user input, it's from
    # equippable_item_types up above
    cursor.execute('''UPDATE "project-deity".follower_equipment
                      SET ''' + class_type.lower() + ''' = %s
                      WHERE follower_id = %s;''',
                   (item_id, follower_id))
    # Return status
    if old_item is None:
        return True
    return item_id
