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

# Returns the lexicon entry for a given term,
# or False if not found
async def get_definition(cursor, search_term):
    cursor.execute('''SELECT definition
                      FROM "project-deity".lexicon
                      WHERE term = %s;''',
                   (search_term.lower(), ))
    results = cursor.fetchone()
    if results is None:
        return False
    else:
        return results["definition"]


# Returns a list contained the  5 most recent definitions
async def get_latest_definitions(cursor):
    cursor.execute('''SELECT term
                      FROM "project-deity".lexicon
                      ORDER BY added DESC, id DESC
                      LIMIT 5''')
    results = cursor.fetchall()
    return [x["term"] for x in results]


# Returns a random term and definition
async def get_random_definition(cursor):
    cursor.execute('''SELECT term, definition
                      FROM "project-deity".lexicon
                      ORDER BY RANDOM()
                      LIMIT 1''')
    results = cursor.fetchone()
    return results["term"], results["definition"]
