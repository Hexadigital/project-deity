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

from datetime import datetime
from datetime import timedelta
import inventory
import item


# Returns a tuple with three items:
# 1. Whether or not it is a new day to login.
# 2. What item was received.
# 3. Whether there was inventory space (the item was added).
# 4. The new login streak.
async def handle_daily_login(cursor, follower_id):
    # Get last login
    cursor.execute('''SELECT * FROM "project-deity".daily_login
                   WHERE follower_id = %s;''',
                   (follower_id, ))
    activity = cursor.fetchone()

    streak = 0
    if activity is None:
        # First time using daily login
        cursor.execute('''INSERT INTO "project-deity".daily_login
                       (follower_id) VALUES (%s);''',
                       (follower_id, ))
    else:
        last_login_date = datetime.date(activity["last_login"])
        todays_date = datetime.date(datetime.now())
        # If today is not a new day...
        if last_login_date == todays_date:
            return (False, None, None, activity["streak"])
        yesterdays_date = todays_date - timedelta(days=1)
        # Did we log in yesterday?
        if last_login_date == yesterdays_date:
            streak = activity["streak"]

    # Find reward based off streak
    streak_day = ((streak + 1) % 7)
    if streak_day == 0:
        streak_day = 7
    cursor.execute('''SELECT item_id FROM "project-deity".login_rewards
                      WHERE day = %s;''',
                   (streak_day, ))
    reward_row = cursor.fetchone()
    # No reward exists for this day...
    if reward_row is None:
        return (True, None, None, streak_day)
    # Create item instance for reward
    item_instance_id = await item.create_item_instance(cursor,
                                                       reward_row["item_id"])
    # Add item to inventory
    add_item_success = await inventory.add_item(cursor, follower_id,
                                                item_instance_id)

    # Was the item added?
    if not add_item_success:
        # Clean up item instance
        await item.delete_item(cursor, item_instance_id)
        return (True, reward_row["item_id"], False, streak_day)

    # Update time and streak
    cursor.execute('''UPDATE "project-deity".daily_login
                      SET last_login = NOW(), streak = %s
                      WHERE follower_id = %s;''',
                   (streak + 1, follower_id))

    return (True, reward_row["item_id"], True, streak + 1)
