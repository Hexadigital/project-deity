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

import math
from PIL import Image


async def render_world_location(x, y, follower_id):
    world = Image.open("images/maps/world.png")
    marker = Image.open("images/maps/marker.png")
    left = x - 75
    upper = y - 75
    right = x + 75
    lower = y + 75
    world_layer = world.crop((left, upper, right, lower))
    marker_layer = Image.new("RGBA", (150, 150))
    marker_layer.paste(marker, (75 - 8, 75 - 16))
    final = Image.alpha_composite(world_layer, marker_layer)
    final = final.resize((300, 300), resample=Image.NEAREST)
    out_path = "./images/renders/world/%s.png" % follower_id
    final.save(out_path)
    return out_path


async def render_follower_location(cursor, follower_info):
    x, y = await get_follower_location(cursor, follower_info)
    await render_world_location(x, y, )
    return "./images/renders/world/%s.png" % follower_info['id']


# Returns the x, y coordinates for the follower
async def get_follower_location(cursor, follower_info):
    cursor.execute('''SELECT ft.start, ft.destination, ft.start_time,
                      now() as current_time,
                      l1.x as start_x, l1.y as start_y,
                      l2.x as dest_x, l2.y as dest_y,
                      l1.name as start_name, l2.name as dest_name
                      FROM "project-deity".follower_travelling ft
                      LEFT JOIN "project-deity".locations l1 ON ft.start = l1.id
                      LEFT JOIN "project-deity".locations l2 ON ft.destination = l2.id
                      WHERE ft.follower_id = %s;''',
                   (follower_info['id'], ))
    travel = cursor.fetchone()
    # Return current location if not travelling
    if travel is None:
        print("%s is not travelling..." % follower_info['name'])
        cursor.execute('''SELECT * FROM "project-deity".locations
                          WHERE id = %s;''',
                       (follower_info['current_location_id'], ))
        location = cursor.fetchone()
        return location
    distance = get_distance(travel['start_x'], travel['start_y'], travel['dest_x'], travel['dest_y'])
    time_elapsed = travel['current_time'] - travel['start_time']
    time_elapsed = math.floor(time_elapsed.total_seconds() / 60)
    print("Follower %s is in transit, been travelling for %smin and needs to travel for %smin" % (follower_info['name'], time_elapsed, distance))
    # Have we reached our location?
    if time_elapsed >= distance:
        # Delete travel record
        cursor.execute('''DELETE FROM "project-deity".follower_travelling
                          WHERE follower_id = %s;''',
                       (follower_info['id'], ))
        # Update follower's location
        cursor.execute('''UPDATE "project-deity".followers
                          SET current_location_id = %s
                          WHERE id = %s;''',
                       (travel['destination'], follower_info['id']))
        return {'id': travel['destination'], 'name': travel['dest_name'], 'x': travel['dest_x'], 'y': travel['dest_y']}
    progress = time_elapsed / distance
    new_x = travel['start_x'] + math.floor((travel['dest_x'] - travel['start_x']) * progress)
    new_y = travel['start_y'] + math.floor((travel['dest_y'] - travel['start_y']) * progress)
    return {'name': 'Travelling from %s to %s' % (travel['start_name'], travel['dest_name']), 'x': new_x, 'y': new_y}


# Returns the five closest locations to the follower
async def get_nearby_locations(cursor, follower_info):
    loc = await get_follower_location(cursor, follower_info)
    cursor.execute('''SELECT * FROM "project-deity".locations''')
    locations = cursor.fetchall()
    distances = []
    for location in locations:
        distance = get_distance(loc['x'], loc['y'], location["x"], location["y"])
        distances.append({"name": location['name'], "distance": distance})
    distances = sorted(distances, key=lambda i: i['distance'])
    if len(distances) > 5:
        distances = distances[:5]
    return distances


# Sets a follower as travelling or returns an error if already travelling
async def travel_to_location(cursor, follower_info, location_name):
    loc = await get_follower_location(cursor, follower_info)
    if 'Travelling' in loc['name']:
        return "ERROR_ALREADY_TRAVELLING"
    cursor.execute('''SELECT * FROM "project-deity".locations
                      WHERE UPPER(name) = UPPER(%s);''',
                   (location_name, ))
    destination = cursor.fetchone()
    if destination is None:
        return "ERROR_BAD_LOCATION"
    cursor.execute('''INSERT INTO "project-deity".follower_travelling
                      (follower_id, start, destination)
                      VALUES (%s, %s, %s);''',
                   (follower_info['id'], loc['id'], destination['id']))
    return destination['name']


# Returns the number of pixels/minutes between two sets of coordinates
def get_distance(x1, y1, x2, y2):
    x3 = abs(x2 - x1)
    y3 = abs(y2 - y1)
    return x3 + y3
