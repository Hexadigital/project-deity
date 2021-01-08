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
from datetime import datetime
from datetime import timedelta
import json
import os
import psycopg2
import psycopg2.extras

import deity
import equipment
import event
import follower
import inventory
import item


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
    print("Testing deity.py...")
    print("1. Populating deities table with sample data.")
    await deity.create_deity(cursor, "Duneyrr")
    await deity.create_deity(cursor, "Dvalinn")
    await deity.create_deity(cursor, "Dainn", discord=976197819574237961)
    print("2. Getting Deity ID by Discord ID.")
    inv_id = await deity.get_deity_by_discord(cursor, 96814651)
    assert inv_id is None
    acc3_id = await deity.get_deity_by_discord(cursor, 976197819574237961)
    assert acc3_id == 3
    print("All tests passed!\n")


async def test_follower(cursor):
    print("Testing follower.py...")
    print("1. Populating follower classes table with sample data.")
    cursor.execute('''INSERT INTO "project-deity".follower_classes
                   (class_name, strength, endurance, intelligence, agility,
                   willpower, hp_bonus, mp_bonus)
                   VALUES ('Moth', 0, 1, 2, 3, 4, 10, 11);''')
    cursor.execute('''INSERT INTO "project-deity".follower_classes
                   (class_name, strength, endurance, intelligence, agility,
                   willpower, hp_bonus, mp_bonus)
                   VALUES ('Octopus', 4, 3, 2, 1, 0, 100, 100);''')
    print("2. Fetching class stats.")
    stat_test = await follower.get_starting_stats(cursor, "Moth")
    assert stat_test["strength"] == 0
    assert stat_test["endurance"] == 1
    assert stat_test["intelligence"] == 2
    assert stat_test["agility"] == 3
    assert stat_test["willpower"] == 4
    print("3. Creating followers.")
    follower_id1 = await follower.create_follower(cursor, "White", "Moth", 1)
    assert follower_id1 == 1
    follower_id2 = await follower.create_follower(cursor, "Blue", "Octopus", 2)
    assert follower_id2 == 2
    follower_id3 = await follower.create_follower(cursor, "Black", "Shadow", 3)
    assert follower_id3 is False
    print("4. Checking HP and MP.")
    follower1_stats = await follower.get_follower_info(cursor, 1)
    follower2_stats = await follower.get_follower_info(cursor, 2)
    assert follower1_stats["hp"] == 14
    assert follower1_stats["max_hp"] == 14
    assert follower1_stats["mp"] == 18
    assert follower1_stats["max_mp"] == 18
    assert follower2_stats["hp"] == 110
    assert follower2_stats["max_hp"] == 110
    assert follower2_stats["mp"] == 107
    assert follower2_stats["max_mp"] == 107
    print("5. Testing currency adjustment.")
    await follower.add_monies(cursor, 1, 50)
    follower1_stats = await follower.get_follower_info(cursor, 1)
    assert follower1_stats["monies"] == 150
    await follower.add_monies(cursor, 1, -75)
    follower1_stats = await follower.get_follower_info(cursor, 1)
    assert follower1_stats["monies"] == 75
    print("6. Testing experience gain and level up.")
    await follower.add_exp(cursor, 1, 50)
    follower1_stats = await follower.get_follower_info(cursor, 1)
    assert follower1_stats["exp"] == 50
    await follower.add_exp(cursor, 1, 51)
    follower1_stats = await follower.get_follower_info(cursor, 1)
    assert follower1_stats["exp"] == 1
    assert follower1_stats["next_level_exp"] == 383
    assert follower1_stats["level"] == 2
    assert follower1_stats["stat_points"] == 3
    assert follower1_stats["hp"] == 16
    assert follower1_stats["max_hp"] == 16
    assert follower1_stats["mp"] == 20
    assert follower1_stats["max_mp"] == 20
    print("All tests passed!\n")


async def test_item(cursor):
    print("Testing item.py...")
    print("1. Populating items table with sample data.")
    cursor.execute('''INSERT INTO "project-deity".items
                      (name, class_type, image, value, weight, rarity,
                      modifier, json_attributes)
                      VALUES ('Orb of Illusion', 'Weapon', 'orb.jpg',
                      10, 10, 0, null, null);''')
    cursor.execute('''INSERT INTO "project-deity".items
                      (name, class_type, image, value, weight, rarity,
                      modifier, json_attributes)
                      VALUES ('Orb of Illusion', 'Weapon', 'orb.jpg',
                      100, 10, 1, 'Bright', null);''')
    cursor.execute('''INSERT INTO "project-deity".items
                      (name, class_type, image, value, weight, rarity,
                      modifier, json_attributes)
                      VALUES ('Ultimate Reward', 'Shield', 'chest.jpg',
                      1000, 100, 3, 'Veiled', null);''')
    print("2. Creating item instances.")
    item1 = await item.create_item_instance(cursor, 1)
    item2 = await item.create_item_instance(cursor, 1)
    item3 = await item.create_item_instance(cursor, 2)
    assert item1 == 1
    assert item2 == 2
    assert item3 == 3
    print("3. Fetching items.")
    item1_dict = await item.get_item(cursor, 1)
    item3_dict = await item.get_item(cursor, 3)
    assert item1_dict["name"] == item3_dict["name"]
    assert item1_dict["class_type"] == item3_dict["class_type"]
    assert item1_dict["image"] == item3_dict["image"]
    assert item1_dict["value"] == 10
    assert item3_dict["value"] == 100
    assert item3_dict["rarity"] > item1_dict["rarity"]
    assert item1_dict["modifier"] is None
    assert item3_dict["modifier"] == 'Bright'
    print("4. Generating text descriptions.")
    item2_desc = await item.get_text_description(cursor, 2)
    item3_desc = await item.get_text_description(cursor, 3)
    assert "\n" not in item2_desc
    assert "a Bright Orb" in item3_desc
    assert "an Orb" in item2_desc
    assert "10 gold" in item2_desc
    print("All tests passed!\n")


async def test_inventory(cursor):
    print("Testing inventory.py...")
    print("1. Add items to inventory.")
    assert await inventory.add_item(cursor, 1, 1) is True
    assert await inventory.add_item(cursor, 1, 1) is True
    assert await inventory.add_item(cursor, 1, 1) is True
    print("2. Attempt to add item to full inventory.")
    # Fill up inventory
    for i in range(0, 21):
        assert await inventory.add_item(cursor, 1, 1) is True
    assert await inventory.add_item(cursor, 1, 1) is False
    print("3. Delete items from inventory.")
    await inventory.delete_item(cursor, 1, 13)
    await inventory.delete_item(cursor, 1, 7)
    print("4. Add items to inventory with gaps.")
    assert await inventory.add_item(cursor, 1, 3) is True
    assert await inventory.add_item(cursor, 1, 1) is True
    assert await inventory.add_item(cursor, 1, 1) is False
    print("All tests passed!\n")


async def test_equipment(cursor):
    print("Testing equipment.py...")
    print("1. Equip item to empty slot.")
    assert await equipment.equip_item(cursor, 1, 1) is True
    print("2. Equip item to filled slot.")
    # Replace (item ID 1) with (slot 2, item ID 1)
    assert await equipment.equip_item(cursor, 1, 2) == 1
    # Replace (item ID 1) with (slot 7, item ID 3)
    assert await equipment.equip_item(cursor, 1, 7) == 1
    # Replace (item ID 3) with (slot 7, item ID 1)
    assert await equipment.equip_item(cursor, 1, 7) == 3
    print("All tests passed!\n")


async def test_event(cursor):
    print("Testing event.py...")
    print("1. Populating login_rewards table with sample data.")
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (1, 1);''')
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (2, 1);''')
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (3, 1);''')
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (4, 1);''')
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (5, 2);''')
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (6, 2);''')
    cursor.execute('''INSERT INTO "project-deity".login_rewards
                      (day, item_id)
                      VALUES (7, 3);''')
    print("2. Test daily login.")
    # First login
    first_login = await event.handle_daily_login(cursor, 2)
    assert first_login[0] is True
    assert first_login[1] == 1
    assert first_login[2] is True
    assert first_login[3] == 1
    # Repeated login within the same day
    repeat_login = await event.handle_daily_login(cursor, 2)
    assert repeat_login[0] is False
    assert repeat_login[1] is None
    assert repeat_login[2] is None
    assert repeat_login[3] == 1
    # Second login in a row
    todays_date = datetime.now()
    yesterdays_date = todays_date - timedelta(days=1)
    cursor.execute('''UPDATE "project-deity".daily_login
                      SET last_login = %s
                      WHERE follower_id = %s;''',
                   (yesterdays_date, 2))
    second_login = await event.handle_daily_login(cursor, 2)
    assert second_login[0] is True
    assert second_login[1] == 1
    assert second_login[2] is True
    assert second_login[3] == 2
    # Repeated login where a streak exists
    repeat_login2 = await event.handle_daily_login(cursor, 2)
    assert repeat_login2[0] is False
    assert repeat_login2[1] is None
    assert repeat_login2[2] is None
    assert repeat_login2[3] == 2
    # Login that breaks a streak
    three_days_ago = todays_date - timedelta(days=3)
    cursor.execute('''UPDATE "project-deity".daily_login
                      SET last_login = %s
                      WHERE follower_id = %s;''',
                   (three_days_ago, 2))
    third_login = await event.handle_daily_login(cursor, 2)
    assert third_login[0] is True
    assert third_login[1] == 1
    assert third_login[2] is True
    assert third_login[3] == 1
    # Seventh day streak
    cursor.execute('''UPDATE "project-deity".daily_login
                      SET last_login = %s, streak = %s
                      WHERE follower_id = %s;''',
                   (yesterdays_date, 6, 2))
    full_week_login = await event.handle_daily_login(cursor, 2)
    assert full_week_login[0] is True
    assert full_week_login[1] == 3
    assert full_week_login[2] is True
    assert full_week_login[3] == 7
    # Login that keeps a streak but resets rewards (aka day 8)
    cursor.execute('''UPDATE "project-deity".daily_login
                      SET last_login = %s
                      WHERE follower_id = %s;''',
                   (yesterdays_date, 2))
    looped_login = await event.handle_daily_login(cursor, 2)
    assert looped_login[0] is True
    assert looped_login[1] == 1
    assert looped_login[2] is True
    assert looped_login[3] == 1
    print("All tests passed!\n")


async def run_tests(conn):
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Run individual tests
    await test_deity(cursor)
    await test_follower(cursor)
    await test_item(cursor)
    await test_inventory(cursor)
    await test_equipment(cursor)
    await test_event(cursor)
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
                            dbname=config["database"] + "_test")
    conn.set_session(autocommit=True)

    cursor = conn.cursor()
    # Cleanup old DB from previous test
    cursor.execute('''DROP SCHEMA IF EXISTS "project-deity" CASCADE;''')
    asyncio.run(create_test_schema(cursor))
    cursor.close()
    conn.close()

    conn = psycopg2.connect(host=config["host"],
                            port=config["port"],
                            user=config["username"],
                            password=config["password"],
                            dbname=config["database"] + "_test")
    conn.set_session(autocommit=True)

    asyncio.run(run_tests(conn))
