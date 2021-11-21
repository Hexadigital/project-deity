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

async def get_shop_in_location(cursor, location_id):
    cursor.execute('''SELECT s.item_id, s.price, i.name, i.class_type,
                      i.image, i.rarity, i.modifier, i.json_attributes, i.description
                      FROM "project-deity".shops s
                      LEFT JOIN "project-deity".items i ON s.item_id = i.id
                      WHERE s.location_id = %s
                      ORDER BY i.name;''',
                   (location_id, ))
    return cursor.fetchall()
