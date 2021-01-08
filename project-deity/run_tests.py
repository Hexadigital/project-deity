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

import asyncio
import json
import os
import psycopg2
import psycopg2.extras

import deity


async def create_test_schema(cursor):
    print("Creating test schema...")
    # Loop through version upgrades
    for sql_file in os.listdir("./database"):
        # Skip non-SQL files
        if sql_file.endswith(".sql"):
            print("Executing %s..." % sql_file)
            cursor.execute(open("./database/" + sql_file, "r").read())
    print("Test schema created!\n")


async def delete_test_schema(cursor):
    print("Deleting test schema...")
    cursor.execute('''DROP SCHEMA "project-deity" CASCADE;''')
    print("Test schema deleted!\n")


async def test_deity(cursor):
    print("1. Populating deities table with sample data.")
    await deity.create_deity(cursor, "Duneyrr")
    await deity.create_deity(cursor, "Dvalinn")
    await deity.create_deity(cursor, "Dainn", discord=976197819574237961)
    print("2. Getting Deity ID by Discord ID.")
    inv_id = await deity.get_deity_by_discord(cursor, 96814651)
    assert inv_id is None
    acc3_id = await deity.get_deity_by_discord(cursor, 976197819574237961)
    assert acc3_id == 3
    pass


async def run_tests(conn):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Run individual tests
    await test_deity(cursor)
    # Clean up
    await delete_test_schema(cursor)
    cursor.close()
    conn.close()


if __name__ == '__main__':
    # Load database config
    with open("config.json", "r") as file:
        config = json.load(file)["database"]

    conn = psycopg2.connect(host=config["host"],
                            port=config["port"],
                            user=config["username"],
                            password=config["password"],
                            dbname=config["schema"] + "_test")
    conn.set_session(autocommit=True)

    cursor = conn.cursor()
    # Cleanup old DB if last test crashed
    cursor.execute('''DROP SCHEMA IF EXISTS "project-deity" CASCADE;''')
    asyncio.run(create_test_schema(cursor))
    cursor.close()
    conn.close()

    conn = psycopg2.connect(host=config["host"],
                            port=config["port"],
                            user=config["username"],
                            password=config["password"],
                            dbname=config["schema"] + "_test")

    asyncio.run(run_tests(conn))
