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


async def render_world_location(follower_id, x, y):
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
    final.save("./images/renders/world/%s.png" % follower_id)
    return "./images/renders/world/%s.png" % follower_id


async def render_follower_location(cursor, follower_info):
    cursor.execute('''SELECT * FROM "project-deity".locations
                      WHERE id = %s;''',
                   (follower_info['current_location_id'], ))
    location = cursor.fetchone()
    rendered = await render_world_location(follower_info['id'], location['x'], location['y'])
    return rendered
