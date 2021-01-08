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

import discord
import json
import os
import psycopg2
import psycopg2.extras

import deity
import follower

client = discord.Client()

with open("config.json", "r") as file:
    config = json.load(file)

conn = psycopg2.connect(host=config["database"]["host"],
                        port=config["database"]["port"],
                        user=config["database"]["username"],
                        password=config["database"]["password"],
                        dbname=config["database"]["database"])
conn.set_session(autocommit=True)
cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

discord_guild_id = config["discord"]["guild"]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    current_version = discord.Game(name="Project Deity v0.1")
    await client.change_presence(activity=current_version)


@client.event
async def on_message(message):
    if message.author.id == client.user.id or message.content[0] != ".":
        return
    # Get deity and follower info
    deity_info = await deity.get_deity_by_discord(cursor, message.author.id)
    follower_info = await follower.get_follower_info_by_deity(cursor, deity_info["id"])
    # Handle help request
    if message.content == ".h" or message.content.startswith('.help'):
        await message.channel.send(("Welcome to Project Deity! "
                                    "You can view the commands here:\n"
                                    "<https://github.com/Frostflake/pro"
                                    "ject-deity/wiki/Discord-Commands>"))
    # Handle registration request
    elif message.content.startswith(".r ") or message.content.startswith(".reg"):
        if message.guild is None or message.guild.id != discord_guild_id:
            await message.channel.send("Registration can only be done in the official server.\nhttps://discord.gg/PaMe88dHbg")
            return
        # Make sure the user isn't registered yet
        if deity_info is not None:
            await message.channel.send("You are already registered!")
            return
        split_msg = message.content.split(" ", 1)
        # Make sure we have a name to use
        if len(split_msg) == 0:
            await message.channel.send("Try '.register NAME' where NAME is your chosen deity name.")
            return
        # Make sure the name isn't already used
        if await deity.check_if_name_taken(cursor, split_msg[1]):
            await message.channel.send("This name is already taken.")
            return
        # Make sure the name is valid
        if not split_msg[1].isalnum():
            await message.channel.send("Deity names must consist of only letters and numbers.")
            return
        if len(split_msg[1]) > 20:
            await message.channel.send("Deity names are capped at 20 characters.")
            return
        # Register the user
        await deity.create_deity(cursor, split_msg[1], discord=message.author.id)
        await message.channel.send("Successfully registered as %s!" % split_msg[1])

    # Handle follower request
    elif message.content.startswith(".f ") or message.content.startswith(".follower"):
        valid_subcommands = ["create", "info"]
        # Ensure the user is registered
        if deity_info is None:
            await message.channel.send("You need to be registered before using this command.\nTry using .register for more details.")
            return
        split_msg = message.content.split(" ", 2)
        # Check for a valid subcommand
        if len(split_msg) == 1 or split_msg[1] not in valid_subcommands:
            subcommand_str = ""
            for sub in valid_subcommands:
                subcommand_str += sub + ", "
            await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
            return
        # Handle follower creation
        if split_msg[1] == "create":
            if follower_info is not None:
                await message.channel.send("You already have a follower!")
                return
            # Did we get a valid input?
            if len(split_msg) == 2 or "," not in split_msg[2]:
                await message.channel.send("You need to specify the name and class of your follower, like so: '.follower create NAME, CLASS'.")
                return
            # Do we have a name and class?
            arguments = [x.strip() for x in split_msg[2].split(",")]
            if len(arguments) != 2:
                await message.channel.send("You need to specify the name and class of your follower, like so: '.follower create NAME, CLASS'.")
                return
            # Is the name valid?
            if not all(x.isalnum() or x.isspace() for x in arguments[0]):
                await message.channel.send("Follower names must consist of only letters, numbers and spaces.")
                return
            if len(arguments[0]) > 20:
                await message.channel.send("Follower names are capped at 20 characters.")
                return
            # Is the class valid?
            if not await follower.check_starting_class(cursor, arguments[1]):
                await message.channel.send("%s is not a valid starting class. You can use '.lexicon Starting Classes' for more info." % arguments[1])
                return
            # Everything looks good, let's create the follower!
            follower_id = await follower.create_follower(cursor, arguments[0], arguments[1], deity_info["id"])
            if not follower_id:
                await message.channel.send("%s is not a valid starting class and caused an error. You can use '.lexicon Starting Classes' for more info." % arguments[1])
                return
            await message.channel.send("%s, a Level 1 %s, has been blessed by %s!" % (arguments[0], arguments[1], deity_info["name"]))
            return
        # Commands below this point require a follower...
        if follower_info is None:
            await message.channel.send("You need to create a follower before you can use this command.\nTry '.follower create'.")
            return
        # Handle follower info request
        if split_msg[1] == "info":
            await message.channel.send("Follower info has not yet been implemented.")
            return


if os.path.isfile("discord.token"):
    with open("discord.token") as file:
        token = file.read()
else:
    with open("discord.token", 'w') as file:
        token = input("Please give me the token for the Discord bot: ")
        token = token.strip()
        file.write(token)

client.run(token)
