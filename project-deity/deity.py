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
async def create_deity(cursor, name, follower, discord=None):
    # Insert row for deity
    cursor.execute('''INSERT INTO deities (name)
                       VALUES (%s)''', (name, ))
    # Add Discord ID if we have one
    if discord is not None:
        row_id = cursor.fetchone()[0]
        cursor.execute('''UPDATE deities
                          SET discord = %s WHERE id = %s''',
                       (discord, row_id))
    return True


# Given a Discord ID, find the associated deity's ID.
# Returns None if nothing is found.
async def get_deity_by_discord(cursor, discord):
    cursor.execute('''SELECT * FROM deities
                      WHERE discord = %s''',
                   (discord, ))
    results = cursor.fetchone()
    if len(results) == 0:
        return None
    else:
        return results[0]
