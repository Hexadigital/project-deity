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

async def get_valid_types(cursor):
    cursor.execute('''SELECT DISTINCT category
                      FROM "project-deity".materials
                      WHERE category IS NOT NULL
                      ORDER BY category;''')
    types = [x["category"] for x in cursor.fetchall()]
    return types


async def get_deity_materials(cursor, deity_id, category=None):
    cursor.execute('''SELECT dm.material_id, dm.quantity,
                      m.category,
                      m.image, m.rarity, m.name
                      FROM "project-deity".deity_materials dm
                      LEFT JOIN "project-deity".materials m
                      ON dm.material_id = m.id
                      WHERE dm.deity_id = %s
                      AND dm.quantity != 0
                      ORDER BY m.name;''',
                   (deity_id, ))
    material_dict = cursor.fetchall()
    return material_dict


async def add_deity_material(cursor, deity_id, material_id, quantity):
    print("Adding %s of material %s to deity %s" % (quantity, material_id, deity_id))
    # Check if the material already exists for this deity
    cursor.execute('''SELECT *
                      FROM "project-deity".deity_materials
                      WHERE deity_id = %s
                      AND material_id = %s;''',
                   (deity_id, material_id))
    existing_material_record = cursor.fetchone()
    # If the deity already has some of this material...
    if existing_material_record is not None:
        new_quantity = min([999, existing_material_record["quantity"] + quantity])
        cursor.execute('''UPDATE "project-deity".deity_materials
                          SET quantity = %s
                          WHERE deity_id = %s
                          AND material_id = %s;''',
                       (new_quantity, deity_id, material_id))
        return new_quantity
    # If the deity never had this material...
    else:
        cursor.execute('''INSERT INTO "project-deity".deity_materials
                          (deity_id, material_id, quantity)
                          VALUES (%s, %s, %s);''',
                       (deity_id, material_id, quantity))
        return quantity


async def update_deity_material_quantity(cursor, deity_id, material_id, quantity):
    print("Setting deity %s material %s quantity to %s" % (deity_id, material_id, quantity))
    cursor.execute('''UPDATE "project-deity".deity_materials
                      SET quantity = %s
                      WHERE deity_id = %s
                      AND material_id = %s;''',
                   (quantity, deity_id, material_id))
    return quantity


async def get_deity_material_quantity_by_name(cursor, deity_id, material_name):
    cursor.execute('''SELECT dm.material_id, dm.quantity, m.name,
                      m.rarity, m.modifier_json
                      FROM "project-deity".deity_materials dm
                      LEFT JOIN "project-deity".materials m ON dm.material_id = m.id
                      WHERE dm.deity_id = %s
                      AND UPPER(m.name) = UPPER(%s)''',
                   (deity_id, material_name))
    return cursor.fetchone()
