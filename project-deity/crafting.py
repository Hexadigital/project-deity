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


# Returns all crafting recipes and information as to whether or not the deity can craft them.
# input#_available = the amount of that material that the player has
# input#_needed = the amount of that material that the player needs
# craftable = whether the player has all of the requirements
async def get_recipes(cursor, deity_id):
    cursor.execute('''SELECT cr.id,
                    (CASE WHEN io.name IS NULL THEN m.name ELSE io.name END) as output_name, cr.output_item, cr.output_material, cr.output_quantity,
                    m1.name as input1_name, cr.input1_item, dm1.quantity AS input1_available, cr.input1_quantity AS input1_needed,
                    m2.name as input2_name, cr.input2_item, dm2.quantity AS input2_available, cr.input2_quantity AS input2_needed,
                    m3.name as input3_name, cr.input3_item, dm3.quantity AS input3_available, cr.input3_quantity AS input3_needed,
                    (CASE
                        WHEN dm1.quantity >= cr.input1_quantity
                        AND (m2.name IS NULL or dm2.quantity >= cr.input2_quantity)
                        AND (m3.name IS NULL or dm3.quantity >= cr.input3_quantity)
                        THEN true
                        ELSE false
                     END) as craftable
                    FROM "project-deity".crafting_recipes cr
                    LEFT JOIN "project-deity".items io ON io.id = cr.output_item
                    LEFT JOIN "project-deity".materials m on m.id = cr.output_material
                    LEFT JOIN "project-deity".materials m1 on m1.id = cr.input1_item
                    LEFT JOIN "project-deity".deity_materials dm1 ON
                        dm1.material_id = cr.input1_item AND dm1.deity_id = %s
                    LEFT JOIN "project-deity".materials m2 on m2.id = cr.input2_item
                    LEFT JOIN "project-deity".deity_materials dm2 ON
                        dm2.material_id = cr.input2_item AND dm2.deity_id = %s
                    LEFT JOIN "project-deity".materials m3 on m3.id = cr.input3_item
                    LEFT JOIN "project-deity".deity_materials dm3 ON
                        dm3.material_id = cr.input3_item AND dm3.deity_id = %s
                    ORDER BY output_name;''',
                   (deity_id, deity_id, deity_id))
    recipes = cursor.fetchall()
    return recipes


async def get_recipe_by_name(cursor, deity_id, craft_name):
    cursor.execute('''SELECT cr.id,
                    (CASE WHEN io.name IS NULL THEN m.name ELSE io.name END) as output_name, cr.output_item, cr.output_material, cr.output_quantity,
                    m1.name as input1_name, cr.input1_item, dm1.quantity AS input1_available, cr.input1_quantity AS input1_needed,
                    m2.name as input2_name, cr.input2_item, dm2.quantity AS input2_available, cr.input2_quantity AS input2_needed,
                    m3.name as input3_name, cr.input3_item, dm3.quantity AS input3_available, cr.input3_quantity AS input3_needed,
                    (CASE
                        WHEN dm1.quantity >= cr.input1_quantity
                        AND (m2.name IS NULL or dm2.quantity >= cr.input2_quantity)
                        AND (m3.name IS NULL or dm3.quantity >= cr.input3_quantity)
                        THEN true
                        ELSE false
                     END) as craftable
                    FROM "project-deity".crafting_recipes cr
                    LEFT JOIN "project-deity".items io ON io.id = cr.output_item
                    LEFT JOIN "project-deity".materials m on m.id = cr.output_material
                    LEFT JOIN "project-deity".materials m1 on m1.id = cr.input1_item
                    LEFT JOIN "project-deity".deity_materials dm1 ON
                        dm1.material_id = cr.input1_item AND dm1.deity_id = %s
                    LEFT JOIN "project-deity".materials m2 on m2.id = cr.input2_item
                    LEFT JOIN "project-deity".deity_materials dm2 ON
                        dm2.material_id = cr.input2_item AND dm2.deity_id = %s
                    LEFT JOIN "project-deity".materials m3 on m3.id = cr.input3_item
                    LEFT JOIN "project-deity".deity_materials dm3 ON
                        dm3.material_id = cr.input3_item AND dm3.deity_id = %s
                    WHERE LOWER((CASE WHEN io.name IS NULL THEN m.name ELSE io.name END)) LIKE LOWER(%s)
                    ORDER BY output_name;''',
                   (deity_id, deity_id, deity_id, craft_name))
    recipe = cursor.fetchone()
    return recipe
