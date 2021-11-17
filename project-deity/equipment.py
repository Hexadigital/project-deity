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

import follower
import inventory
import item
import json
from PIL import Image

equippable_item_types = ["Accessory", "Helmet", "Ring", "Weapon", "Armor",
                         "Shield", "Gloves", "Legs", "Boots"]


# Returns the name of the equipped item if successful
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
        return "ERROR_NOT_EQUIPPABLE"
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
                       (old_item, follower_id, slot_num))
    else:
        # If we aren't reusing the inventory slot, then
        # we need to remove the item we're equipping
        # from the inventory.
        cursor.execute('''DELETE FROM "project-deity".follower_inventories
                          WHERE follower_id = %s
                          AND slot_num = %s;''',
                       (follower_id, slot_num))
    # Equip new item
    # Yes, yes, string concatenation for SQL is a sin
    # but in this case it's not user input, it's from
    # equippable_item_types up above
    cursor.execute('''UPDATE "project-deity".follower_equipment
                      SET ''' + class_type.lower() + ''' = %s
                      WHERE follower_id = %s;''',
                   (item_id, follower_id))
    new_equip_name = await item.get_item(cursor, item_id)
    return new_equip_name['name']


async def unequip_item(cursor, follower_id, equipment_slot):
    # What is in this slot?
    cursor.execute('''SELECT *
                      FROM "project-deity".follower_equipment
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    equipped_item = cursor.fetchone()[equipment_slot]
    if equipped_item is None:
        return "ERROR_SLOT_EMPTY"
    # Add it to the inventory
    inv_result = await inventory.add_item(cursor, follower_id, equipped_item)
    if not inv_result:
        return "ERROR_NO_INV_SPACE"
    # Remove it from equipment
    cursor.execute('''UPDATE "project-deity".follower_equipment
                      SET ''' + equipment_slot + ''' = NULL
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    item_inst = await item.get_item(cursor, equipped_item)
    return item_inst['name']


# Renders a path to a rendered inventory image
async def generate_equipment_image(cursor, follower_id):
    cursor.execute('''SELECT *
                      FROM "project-deity".follower_equipment
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    equips = cursor.fetchone()

    follower_info = await follower.get_follower_info(cursor, follower_id)

    render_order = [x.lower() for x in equippable_item_types]
    # Generate image
    background = Image.open("images/bgs/equipment/" + follower_info['class_name'] + ".png")
    backslots = Image.new("RGBA", (150, 150))
    result = Image.new("RGBA", (150, 150))
    columncount = 0
    rowcount = 0
    for i in range(0, 9):
        x = 24 + (columncount * 34)
        y = 24 + (rowcount * 34)
        item_rarity = 0
        # Add item image if we have an item
        if equips[render_order[i]] is not None:
            item_inst = await item.get_item(cursor, equips[render_order[i]])
            img = Image.open("./images/items/" + item_inst['image'])
            result.paste(img, (x, y, x + 34, y + 34))
            item_rarity = item_inst['rarity']
        img3 = Image.open("./images/slots/" + str(item_rarity) + ".png")
        backslots.paste(img3, (x, y, x + 34, y + 34))
        columncount += 1
        if columncount == 3:
            columncount = 0
            rowcount += 1
    # Combine layers and save
    highlayer = Image.alpha_composite(backslots, result)
    Image.alpha_composite(background.convert('RGBA'), highlayer).save("./images/renders/equipment/%s.png" % follower_id)
    return "./images/renders/equipment/%s.png" % follower_id


# Gives a total for equipment effects
async def get_stats(cursor, follower_id):
    cursor.execute('''SELECT *
                      FROM "project-deity".follower_equipment
                      WHERE follower_id = %s;''',
                   (follower_id, ))
    equips = cursor.fetchone()

    buffs = {}
    for column in equips.keys():
        if column != 'follower_id' and equips[column] is not None:
            item_inst = await item.get_item(cursor, equips[column])
            item_json = json.loads(item_inst['json_attributes'])
            # Handle base attributes
            for attribute in item_json["Base"].keys():
                amount = int(item_json["Base"][attribute])
                # Add to buffs
                if attribute not in buffs.keys():
                    buffs[attribute] = amount
                else:
                    buffs[attribute] = buffs[attribute] + amount
            # Handle modifier
            if "Modifier" in item_json.keys():
                attribute = item_json["Modifier"]["Effects"]
                amount = int(item_json["Modifier"]["Amount"])
                # Add to buffs
                if attribute not in buffs.keys():
                    buffs[attribute] = amount
                else:
                    buffs[attribute] = buffs[attribute] + amount
    return buffs
