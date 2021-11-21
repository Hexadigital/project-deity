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


async def get_follower_quests(cursor, follower_info):
    cursor.execute('''SELECT fq.id as fq_id, q.*, fq.quest_progress, fq.quest_status
                      FROM "project-deity".follower_quests fq
                      LEFT JOIN "project-deity".quests q ON fq.quest_id = q.id
                      WHERE fq.follower_id = %s
                      ORDER BY fq.id;''',
                   (follower_info['id'], ))
    quest_list = cursor.fetchall()
    return quest_list


async def add_follower_quest(cursor, follower_info, quest_id):
    quest_list = await get_follower_quests(cursor, follower_info)
    if quest_id in [q['id'] for q in quest_list]:
        return "ERROR_ALREADY_HAVE_QUEST"
    if len(quest_list) >= 3:
        return "ERROR_TOO_MANY_QUESTS"
    cursor.execute('''SELECT * FROM "project-deity".quests
                      WHERE id = %s;''',
                   (quest_id, ))
    quest_info = cursor.fetchone()
    if quest_info['quest_type'] in ['Slayer', 'Foraging', 'Woodcutting']:
        status = 'In Progress'
    else:
        status = 'Not Started'
    cursor.execute('''INSERT INTO "project-deity".follower_quests
                      (follower_id, quest_id, quest_status)
                      VALUES (%s, %s, %s);''',
                   (follower_info['id'], quest_id, status))
    return quest_info['name']
