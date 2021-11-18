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

from PIL import Image


async def render_world_location(x, y, out_path):
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
    final.save(out_path)


async def render_follower_location(cursor, follower_info):
    x, y = await get_follower_location(cursor, follower_info)
    await render_world_location(x, y, "./images/renders/world/%s.png" % follower_info['id'])
    return "./images/renders/world/%s.png" % follower_info['id']


# Returns the x, y coordinates for the follower
async def get_follower_location(cursor, follower_info):
    cursor.execute('''SELECT * FROM "project-deity".locations
                      WHERE id = %s;''',
                   (follower_info['current_location_id'], ))
    location = cursor.fetchone()
    return location['x'], location['y']


# Returns the five closest locations to the follower
async def get_nearby_locations(cursor, follower_info):
    current_x, current_y = await get_follower_location(cursor, follower_info)
    cursor.execute('''SELECT * FROM "project-deity".locations
                      WHERE id != %s;''',
                   (follower_info['current_location_id'], ))
    locations = cursor.fetchall()
    distances = []
    for location in locations:
        distance = get_distance(current_x, current_y, location["x"], location["y"])
        distances.append({"name": location['name'], "distance": distance})
    distances = sorted(distances, key=lambda i: i['distance'])
    if len(distances) > 5:
        distances = distances[:5]
    return distances


# Returns the number of pixels/minutes between two sets of coordinates
def get_distance(x1, y1, x2, y2):
    x3 = abs(x2 - x1)
    y3 = abs(y2 - y1)
    return x3 + y3
