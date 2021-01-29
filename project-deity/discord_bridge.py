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
import hashlib
import json
import os
import psycopg2
import psycopg2.extras

import deity
import event
import follower
import inventory
import item
import lexicon
import material

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
    if message.author.id == client.user.id or not message.content.startswith("."):
        return
    # Get deity and follower info
    deity_info = await deity.get_deity_by_discord(cursor, message.author.id)
    if deity_info is not None:
        follower_info = await follower.get_follower_info_by_deity(cursor, deity_info["id"])
    else:
        follower_info = None
    # HELP COMMAND
    if message.content == ".h" or message.content.startswith('.help'):
        await message.channel.send(("Welcome to Project Deity! "
                                    "You can view the commands here:\n"
                                    "<https://github.com/Frostflake/pro"
                                    "ject-deity/wiki/Discord-Commands>"))
    # REGISTER COMMAND
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
        if len(split_msg) == 1:
            await message.channel.send("Try '.register NAME' where NAME is your chosen deity name.")
            return
        # Make sure the name isn't already used
        if await deity.check_if_name_taken(cursor, split_msg[1]):
            await message.channel.send("This name is already taken.")
            return
        # Make sure the name is valid
        if not all(x.isalnum() or x.isspace() for x in split_msg[1]):
            await message.channel.send("Follower names must consist of only letters, numbers and spaces.")
            return
        if len(split_msg[1]) > 20:
            await message.channel.send("Deity names are capped at 20 characters.")
            return
        # Register the user
        await deity.create_deity(cursor, split_msg[1], discord=message.author.id)
        await message.channel.send("Successfully registered as %s!" % split_msg[1])

    # FOLLOWER COMMAND
    elif message.content.startswith(".f ") or message.content.startswith(".follower"):
        valid_subcommands = ["abandon", "avatar", "create", "info"]
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
            await message.channel.send("%s, a Level 1 %s, has begun to worship %s!" % (arguments[0], arguments[1], deity_info["name"]))
            return
        # Commands below this point require a follower...
        if follower_info is None:
            await message.channel.send("You need to create a follower before you can use this command.\nTry '.follower create'.")
            return
        if split_msg[1] == "abandon":
            abandon_code = "goodbyemyfriend" + str(follower_info["id"])
            abandon_code = hashlib.md5(abandon_code.encode()).hexdigest()
            if len(split_msg) == 2:
                response = "Are you sure you want to abandon %s? All stats, items, equipment, and progress will be lost. You cannot get them back.\n\n`If you are sure, type '.follower abandon %s' and your follower will be abandoned.`" % (follower_info["name"], abandon_code)
            elif len(split_msg) == 3:
                if split_msg[2] == abandon_code:
                    name, level, class_name = await follower.abandon_follower(cursor, follower_info["id"])
                    response = "%s, a Level %s %s, has been abandoned by %s. Faithless, they now wander this world with no guidance or support." % (name, level, class_name, deity_info["name"])
                else:
                    response = "Incorrect abandonment code."
            await message.channel.send(response)
        # Handle follower info request
        if split_msg[1] == "info":
            if len(split_msg) == 3:
                other_info = await follower.get_follower_info_by_name(cursor, split_msg[2])
                if other_info is None:
                    await message.channel.send("No follower could be found with that name.")
                    return
                follower_card = await follower.render_follower_card(cursor, other_info)
                await message.channel.send(file=discord.File(follower_card))
                return
            follower_card = await follower.render_follower_card(cursor, follower_info)
            await message.channel.send(file=discord.File(follower_card))
            return
        # Handle follower avatar
        if split_msg[1] == "avatar":
            avatar_list = await follower.get_avatars(cursor, deity_info["id"])
            if len(split_msg) == 3:
                for avatar in avatar_list:
                    if avatar["name"].lower() == split_msg[2].strip().lower():
                        await follower.set_avatar(cursor, follower_info["id"], avatar["filename"])
                        await message.channel.send("Avatar updated successfully.")
                        return
                await message.channel.send("No avatar could be found with that name.")
                return
            response = "Available avatars: "
            for avatar in avatar_list:
                response += avatar["name"] + ", "
            await message.channel.send(response[:-2] + "\n\nTo set your avatar, use `.follower avatar AVATAR_NAME`.")
            return
    # DAILY COMMAND
    elif message.content == ".d" or message.content.startswith(".daily"):
        if follower_info is None:
            await message.channel.send("You need to create a follower before you can use this command.\nTry '.follower create'.")
            return
        daily_results = await event.handle_daily_login(cursor, follower_info["id"])
        if not daily_results[0]:
            await message.channel.send("You already claimed your daily for today! It will reset at midnight EST.")
            return
        if not daily_results[2]:
            await message.channel.send("Your inventory is full! Clean it out before claiming your daily.")
            return
        # Get item info
        reward_info = await item.get_master_item(cursor, daily_results[1])
        response_text = ""
        if reward_info["modifier"] is not None:
            response_text += "You have received one %s %s!" % (reward_info["modifier"], reward_info["name"])
        else:
            response_text += "You have received one %s!" % reward_info["name"]
        if (daily_results[3] % 7) == 0:
            response_text += " The weekly rewards will now reset."
        response_text += "\nYour current login streak is: **%s**" % daily_results[3]
        await message.channel.send(response_text)
        return
    # CHEATS COMMAND
    elif message.content.startswith(".cheats"):
        # Joke command?
        await message.channel.send("This command can only be used if you're accessing Project Deity via a Bitcoin ATM.")
        return
    # LEXICON COMMAND
    elif message.content.startswith(".l ") or message.content.startswith(".lex") or message.content.startswith(".lookup"):
        split_msg = message.content.split(" ", 1)
        if len(split_msg) == 1:
            await message.channel.send("You need to specify the term to search for, like so:\n.lexicon SEARCH TERM\nYou can also use 'latest' to see the latest additions, or 'random' to get a random entry.")
            return
        elif split_msg[1].lower() == "latest":
            lexi = await lexicon.get_latest_definitions(cursor)
            response_text = "The latest additions to the lexicon are:\n"
            for x in lexi:
                response_text += x + ", "
            await message.channel.send(response_text[:-2])
        elif split_msg[1].lower() == "random":
            term, definition = await lexicon.get_random_definition(cursor)
            await message.channel.send("**%s**\n%s" % (term, definition))
        else:
            lexi = await lexicon.get_definition(cursor, split_msg[1])
            if not lexi:
                await message.channel.send("No definition could be found for %s." % split_msg[1])
                return
            await message.channel.send(lexi)
            return
    # INVENTORY COMMAND
    elif message.content == ".i" or message.content.startswith(".i ") or message.content.startswith(".inv"):
        valid_subcommands = ["info", "open"]
        if follower_info is None:
            await message.channel.send("You need to create a follower before you can use this command.\nTry '.follower create'.")
            return
        split_msg = message.content.split(" ", 2)
        if len(split_msg) == 1:
            inventory_render = await inventory.generate_inventory_image(cursor, follower_info["id"])
            response = "%s has %s Gold." % (follower_info["name"], follower_info["monies"])
            await message.channel.send(response, file=discord.File(inventory_render))
            return
        # Check for a valid subcommand
        elif split_msg[1] not in valid_subcommands:
            subcommand_str = ""
            for sub in valid_subcommands:
                subcommand_str += sub + ", "
            await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
            return
        elif split_msg[1].lower() == "info":
            if not len(split_msg) == 3 or "," not in split_msg[2]:
                await message.channel.send("You need to specify the item to look at, like so: '.inventory info ROW,COLUMN'\nFor example, to view the first item in your inventory, you would use '.inventory info 1,1'")
                return
            row, column = split_msg[2].split(",", 1)
            # Remove whitespace
            row = row.strip()
            column = column.strip()
            # Ensure row/column are valid
            if not row.isdigit() or not column.isdigit() or int(row) > 100 or int(column) > 100:
                await message.channel.send("You need to specify the item to look at, like so: '.inventory info ROW,COLUMN'\nFor example, to view the first item in your inventory, you would use '.inventory info 1,1'")
                return
            # Calculate the slot ID
            slot_id = int(column) + ((int(row) - 1) * follower_info["inv_height"])
            # Figure out what item to look up
            item_instance_id = await inventory.get_item_in_slot(cursor, follower_info["id"], slot_id)
            if item_instance_id is None:
                await message.channel.send("That inventory slot is empty!")
                return
            # Get the item's information
            item_info = await item.get_item(cursor, item_instance_id["item_id"])
            if item_info["modifier"] is not None:
                response = "Name: %s %s\n" % (item_info["modifier"], item_info["name"])
            else:
                response = "Name: %s\n" % item_info["name"]
            response += "Type: %s\n\n" % item_info["class_type"]
            response += item_info["description"]
            await message.channel.send(response)
            return
        elif split_msg[1].lower() == "open":
            if not len(split_msg) == 3 or "," not in split_msg[2]:
                await message.channel.send("You need to specify the item to open, like so: '.inventory open ROW,COLUMN'\nFor example, to open the first item in your inventory, you would use '.inventory open 1,1'")
                return
            row, column = split_msg[2].split(",", 1)
            # Remove whitespace
            row = row.strip()
            column = column.strip()
            # Ensure row/column are valid
            if not row.isdigit() or not column.isdigit() or int(row) > 100 or int(column) > 100:
                await message.channel.send("You need to specify the item to open, like so: '.inventory open ROW,COLUMN'\nFor example, to view the first item in your inventory, you would use '.inventory open 1,1'")
                return
            # Calculate the slot ID
            slot_id = int(column) + ((int(row) - 1) * follower_info["inv_height"])
            # Figure out what item to look up
            item_instance = await inventory.get_item_in_slot(cursor, follower_info["id"], slot_id)
            if item_instance is None:
                await message.channel.send("Despite your best efforts, you are unable to open something that doesn't exist.")
                return
            item_info = await item.get_item(cursor, item_instance["item_id"])
            reward_id, quantity, reward_type, reward_name = await item.get_container_reward(cursor, item_info["master_item_id"])
            if reward_id is None:
                if item_info["modifier"] is None:
                    await message.channel.send("You try with all of your might, but are unable to open the %s." % item_info["name"])
                    return
                else:
                    await message.channel.send("You try with all of your might, but are unable to open the %s %s." % (item_info["modifier"], item_info["name"]))
                return
            pluralism = ""
            if quantity > 1:
                pluralism = "s"
            # Is this gold?
            if reward_id == 0:
                await follower.add_monies(cursor, follower_info["id"], quantity)
                if item_info["modifier"] is None:
                    await message.channel.send("You open the %s and find %s Gold!" % (item_info["name"], quantity))
                else:
                    await message.channel.send("You open the %s %s and find %s Gold!" % (item_info["modifier"], item_info["name"], quantity))
            # Is this a material?
            elif reward_type == "Material":
                await material.add_deity_material(cursor, deity_info["id"], reward_id, quantity)
                if item_info["modifier"] is None:
                    await message.channel.send("You open the %s and find %sx %s%s!" % (item_info["name"], quantity, reward_name, pluralism))
                else:
                    await message.channel.send("You open the %s %s and find %sx %s%s!" % (item_info["modifier"], item_info["name"], quantity, reward_name, pluralism))
            # TODO: Is this an item?
            else:
                pass
            # Delete inventory item
            await inventory.delete_item(cursor, follower_info["id"], slot_id)
            # Delete item instance
            await item.delete_item(cursor, item_instance["item_id"])
            return
    elif message.content == ".m" or message.content.startswith(".m ") or message.content.startswith(".mat"):
        valid_subcommands = ["categories", "view"]
        split_msg = message.content.split(" ", 2)
        if len(split_msg) == 1:
            subcommand_str = ""
            for sub in valid_subcommands:
                subcommand_str += sub + ", "
            await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
            return
        # Check for a valid subcommand
        elif split_msg[1] not in valid_subcommands:
            subcommand_str = ""
            for sub in valid_subcommands:
                subcommand_str += sub + ", "
            await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
            return
        elif split_msg[1].lower() == "categories":
            category_str = "Here are the material categories: "
            for category in await material.get_valid_types(cursor):
                category_str += category + ", "
            await message.channel.send(category_str[:-2])
            return
        elif split_msg[1].lower() == "view":
            if len(split_msg) == 2:
                # Display all
                material_dict = await material.get_deity_materials(cursor, deity_info["id"])
                material_string = ""
                for material_row in material_dict:
                    material_string += str(material_row["quantity"]) + "x " + material_row["name"]
                    if material_row["quantity"] > 1:
                        material_string += "s"
                    material_string += ", "
                await message.channel.send("You have: " + material_string[:-2])
                return
            else:
                # Display chosen category
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
