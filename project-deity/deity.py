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

# Create a deity and return success status
async def create_deity(cursor, name, discord=None):
    # Insert row for deity
    cursor.execute('''INSERT INTO "project-deity".deities
                      (name)
                      VALUES (%s)
                      RETURNING id;''', (name, ))
    # Add Discord ID if we have one
    if discord is not None:
        row_id = cursor.fetchone()["id"]
        cursor.execute('''UPDATE "project-deity".deities
                          SET discord = %s
                          WHERE id = %s;''',
                       (discord, row_id))
    return True


# Given a Discord ID, find the associated deity's info.
# Returns None if nothing is found.
async def get_deity_by_discord(cursor, discord):
    cursor.execute('''SELECT id, name
                      FROM "project-deity".deities
                      WHERE discord = %s;''',
                   (discord, ))
    results = cursor.fetchone()
    return results


async def get_deity_by_id(cursor, deity_id):
    cursor.execute('''SELECT id, name
                      FROM "project-deity".deities
                      WHERE id = %s;''',
                   (deity_id, ))
    results = cursor.fetchone()
    return results


async def check_if_name_taken(cursor, name):
    cursor.execute('''SELECT id
                      FROM "project-deity".deities
                      WHERE name = %s;''',
                   (name, ))
    results = cursor.fetchone()
    if results is None:
        return False
    else:
        return True
