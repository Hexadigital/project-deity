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

from datetime import date, datetime, timedelta, time
import discord
import hashlib
import json
import math
import os
import psycopg2
import psycopg2.extras

import crafting
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
valid_nondeity_commands = [".r", ".register", ".h", ".help", ".l", ".lexicon"]
valid_deity_commands = [".r", ".register", ".h", ".help", ".f", ".follower", ".d", ".daily", ".s", ".stats", ".l", ".lexicon"]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    current_version = discord.Game(name="Project Deity v0.1b")
    await client.change_presence(activity=current_version)


async def handle_registration(message):
    if message.guild is None or message.guild.id != discord_guild_id:
        await message.channel.send("Registration can only be done in the official server.\nhttps://discord.gg/PaMe88dHbg")
    split_msg = [x.strip() for x in message.content.split(" ", 1)]
    if len(split_msg) == 1:
        await message.channel.send("Try '.register NAME' where NAME is your chosen deity name.")
    elif await deity.check_if_name_taken(cursor, split_msg[1]):
        await message.channel.send("This name is already taken.")
    elif not all(x.isalnum() or x.isspace() for x in split_msg[1]):
        await message.channel.send("Follower names must consist of only letters, numbers and spaces.")
    elif len(split_msg[1]) > 20:
        await message.channel.send("Deity names are capped at 20 characters.")
    await deity.create_deity(cursor, split_msg[1], discord=message.author.id)
    await message.channel.send("Successfully registered as %s!" % split_msg[1])


async def handle_follower_creation(message, deity_info, follower_info, split_msg):
    # TODO: Check deity follower cap
    if follower_info is not None:
        await message.channel.send("You already have the max number of followers!")
        return
    # Check argument count
    elif len(split_msg) == 2 or "," not in split_msg[2]:
        await message.channel.send("You need to specify the name and class of your follower, like so: '.follower create NAME, CLASS'.")
        return
    # Check arguments
    arguments = [x.strip() for x in split_msg[2].split(",")]
    if len(arguments) != 2:
        await message.channel.send("You need to specify the name and class of your follower, like so: '.follower create NAME, CLASS'.")
    # Check name validity
    elif not all(x.isalnum() or x.isspace() for x in arguments[0]):
        await message.channel.send("Follower names must consist of only letters, numbers and spaces.")
    # Check name length
    elif len(arguments[0]) > 20:
        await message.channel.send("Follower names are capped at 20 characters.")
    # Check class validity
    elif not await follower.check_starting_class(cursor, arguments[1]):
        await message.channel.send("%s is not a valid starting class. You can use '.lexicon Starting Classes' for more info." % arguments[1])
    else:
        # Create follower
        follower_id = await follower.create_follower(cursor, arguments[0], arguments[1], deity_info["id"])
        if not follower_id:
            await message.channel.send("Something went wrong. Please ping an admin and we will look into this.")
        else:
            await message.channel.send("%s, a Level 1 %s, has begun to worship %s!" % (arguments[0], arguments[1], deity_info["name"]))


async def handle_follower_abandonment(message, deity_info, follower_info, split_msg):
    if follower_info is None:
        await message.channel.send("You have no followers!")
    else:
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


async def handle_follower_avatar(message, deity_info, follower_info, split_msg):
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


async def handle_follower_title(message, deity_info, follower_info, split_msg):
    title_list = await follower.get_titles(cursor, follower_info["id"])
    if len(split_msg) == 3:
        for title in title_list:
            if title["title"].lower() == split_msg[2].strip().lower():
                await follower.set_title(cursor, follower_info["id"], title["title"])
                await message.channel.send("Title updated successfully.")
                return
        await message.channel.send("No title could be found with that name.")
        return
    response = "Available titles: "
    for title in title_list:
        response += title["title"] + ", "
    await message.channel.send(response[:-2] + "\n\nTo set your title, use `.follower title TITLE_NAME`.")


async def handle_follower(message, deity_info, follower_info):
    valid_subcommands = ["abandon", "avatar", "create", "switch", "title"]
    split_msg = message.content.split(" ", 2)
    if len(split_msg) == 1 or split_msg[1] not in valid_subcommands:
        subcommand_str = ""
        for sub in valid_subcommands:
            subcommand_str += sub + ", "
        await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
    elif split_msg[1] == "create":
        await handle_follower_creation(message, deity_info, follower_info, split_msg)
    elif split_msg[1] == "abandon":
        await handle_follower_abandonment(message, deity_info, follower_info, split_msg)
    elif split_msg[1] == "avatar":
        await handle_follower_avatar(message, deity_info, follower_info, split_msg)
    elif split_msg[1] == "title":
        await handle_follower_title(message, deity_info, follower_info, split_msg)
    elif split_msg[1] == "switch":
        await message.channel.send("You do not have a follower to switch to!")


async def handle_stats(message, deity_info, follower_info):
    valid_subcommands = []
    split_msg = message.content.split(" ", 1)
    if follower_info is None:
        await message.channel.send("You need a follower before you can use this command.")
    elif len(split_msg) == 1:
        follower_card = await follower.render_follower_card(cursor, follower_info)
        await message.channel.send(file=discord.File(follower_card))
    elif len(split_msg) == 2 and split_msg[1] not in valid_subcommands:
        other_info = await follower.get_follower_info_by_name(cursor, split_msg[1])
        if other_info is None:
            await message.channel.send("No follower could be found with that name.")
            return
        follower_card = await follower.render_follower_card(cursor, other_info)
        await message.channel.send(file=discord.File(follower_card))


async def handle_daily(message, deity_info, follower_info):
    valid_subcommands = ["info"]
    split_msg = message.content.split(" ", 1)
    if follower_info is None:
        await message.channel.send("You need a follower before you can use this command.")
    elif len(split_msg) > 1 and split_msg[1] not in valid_subcommands:
        subcommand_str = ""
        for sub in valid_subcommands:
            subcommand_str += sub + ", "
        await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
    elif len(split_msg) == 1:
        daily_results = await event.handle_daily_login(cursor, follower_info["id"])
        if not daily_results[0]:
            total_seconds = (datetime.combine(date.today() + timedelta(1), time()) - datetime.now()).seconds
            m, s = divmod(total_seconds, 60)
            h, m = divmod(m, 60)
            time_remaining = ""
            if s != 0:
                time_remaining = str(s) + "s"
            if m != 0:
                time_remaining = str(m) + "m" + time_remaining
            if h != 0:
                time_remaining = str(h) + "h" + time_remaining
            await message.channel.send("You already claimed your daily for today! It will reset in %s." % time_remaining)
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
    elif split_msg[1] == "info":
        await message.channel.send("Current daily reward: Normal.")


async def handle_lexicon(message):
    split_msg = message.content.split(" ", 1)
    if len(split_msg) == 1:
        await message.channel.send("You need to specify the term to search for, like so:\n.lexicon SEARCH TERM\nYou can also use 'latest' to see the latest additions, or 'random' to get a random entry.")
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


async def handle_craft(message, deity_info, follower_info):
    valid_subcommands = ["craft", "help", "list"]
    if follower_info is None:
        await message.channel.send("You need a follower before you can use this command.")
        return
    split_msg = [x.strip() for x in message.content.split(" ", 2)]
    if len(split_msg) == 1 or split_msg[1] not in valid_subcommands:
        subcommand_str = ""
        for sub in valid_subcommands:
            subcommand_str += sub + ", "
        await message.channel.send("You can use the following subcommands: %s." % subcommand_str[:-2])
    elif split_msg[1].lower() == "craft":
        if len(split_msg) != 3:
            await message.channel.send("You need to specify the item to craft, such as '.c craft Wooden Sword'.")
            return
        if "," in split_msg[2]:
            await message.channel.send("Crafting using modifiers is currently disabled.")
            return
        recipe = await crafting.get_recipe_by_name(cursor, deity_info["id"], split_msg[2])
        if recipe is None:
            await message.channel.send("This does not appear to be a valid crafting recipe.")
            return
        if not recipe["craftable"]:
            await message.channel.send("You do not have the materials needed to craft this!")
            return
        # await message.channel.send(str(dict(recipe)))
        if recipe["output_material"] is None:
            await message.channel.send("Item crafting is currently disabled. Try crafting a material.")
            return
        # Subtract materials
        await material.update_deity_material_quantity(cursor, deity_info["id"], recipe["input1_item"], recipe["input1_available"] - recipe["input1_needed"])
        if recipe["input2_item"] is not None:
            await material.update_deity_material_quantity(cursor, deity_info["id"], recipe["input2_item"], recipe["input2_available"] - recipe["input2_needed"])
        if recipe["input3_item"] is not None:
            await material.update_deity_material_quantity(cursor, deity_info["id"], recipe["input3_item"], recipe["input3_available"] - recipe["input3_needed"])
        # Add resulting material
        await material.add_deity_material(cursor, deity_info["id"], recipe["output_material"], recipe["output_quantity"])
        await message.channel.send("You successfully crafted %sx %s!" % (recipe["output_quantity"], recipe["output_name"]))
    elif split_msg[1].lower() == "help":
        help_text = "Crafting is a system by which you can combine materials into new materials or into items.\n"
        help_text += "You can view the list of crafting recipes via '.c list', with an optional page number such as '.c list 2'.\n\n"
        help_text += "To craft an item, just type '.c craft item name', such as '.c craft Wooden Sword'.\n"
        help_text += "To add a modifier, add the modifier material with a comma, such as '.c craft Wooden Sword, Small Fang'."
        await message.channel.send(help_text)
    elif split_msg[1].lower() == "list":
        recipes = await crafting.get_recipes(cursor, deity_info["id"])
        page = 1
        total_pages = int(math.ceil(len(recipes) / 10))
        if len(split_msg) == 3 and split_msg[2].isnumeric():
            page = int(split_msg[2])
            if page > total_pages:
                await message.channel.send("This page does not exist.")
                return
        start_point = (page - 1) * 10
        end_point = int(page) * 10
        if end_point > len(recipes):
            recipes = recipes[start_point:]
        else:
            recipes = recipes[start_point:end_point]
        recipe_list = "```"
        for recipe in recipes:
            if recipe["craftable"]:
                recipe_list += "\n\U00002714 "
            else:
                recipe_list += "\n\U00002716 "
            recipe_list += str(recipe["output_quantity"]) + "x " + recipe["output_name"] + " "
            recipe_list += "(" + str(recipe["input1_needed"]) + " " + recipe["input1_name"]
            if recipe["input2_name"] is not None:
                recipe_list += ", " + str(recipe["input2_needed"]) + " " + recipe["input2_name"]
            if recipe["input3_name"] is not None:
                recipe_list += ", " + str(recipe["input3_needed"]) + " " + recipe["input3_name"]
            recipe_list += ")"
        await message.channel.send(recipe_list + "\n\nPage " + str(page) + " of " + str(total_pages) + "```")


async def handle_inventory(message, deity_info, follower_info):
    valid_subcommands = ["equip", "info", "open", "use"]
    if follower_info is None:
        await message.channel.send("You need a follower before you can use this command.")
        return
    split_msg = [x.strip() for x in message.content.split(" ", 2)]
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
    elif split_msg[1].lower() == "equip":
        await message.channel.send("Equipping items is not supported at this time.")
    elif split_msg[1].lower() == "use":
        if not len(split_msg) == 3:
            await message.channel.send("You need to specify the item to look at, like so: '.inventory info SLOT'\nFor example, to view the first item in your inventory, you would use '.inventory info 1'")
            return
        requested_slot = split_msg[2]
        # Ensure row/column are valid
        if not requested_slot.isdigit() or int(requested_slot) > 250 or int(requested_slot) <= 0:
            await message.channel.send("That inventory slot is empty!")
            return
        # Figure out what item to look up
        item_instance_id = await inventory.get_item_in_slot(cursor, follower_info["id"], requested_slot)
        if item_instance_id is None:
            await message.channel.send("That inventory slot is empty!")
            return
        # Get the item's information
        item_info = await item.get_item(cursor, item_instance_id["item_id"])
        if item_info["class_type"] in ["Weapon", "Accessory", "Helmet", "Ring", "Armor", "Shield", "Gloves", "Legs", "Boots"]:
            await message.channel.send("This item cannot be used. Maybe you meant to equip it?")
        elif item_info["class_type"] in ["Container"]:
            await message.channel.send("This item cannot be used. Maybe you meant to open it?")
        else:
            await message.channel.send("Using items is not supported at this time.")
    elif split_msg[1].lower() == "info":
        if not len(split_msg) == 3:
            await message.channel.send("You need to specify the item to look at, like so: '.inventory info SLOT'\nFor example, to view the first item in your inventory, you would use '.inventory info 1'")
            return
        requested_slot = split_msg[2]
        # Ensure row/column are valid
        if not requested_slot.isdigit() or int(requested_slot) > 250 or int(requested_slot) <= 0:
            await message.channel.send("That inventory slot is empty!")
            return
        # Figure out what item to look up
        item_instance_id = await inventory.get_item_in_slot(cursor, follower_info["id"], requested_slot)
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
        if not len(split_msg) == 3:
            await message.channel.send("You need to specify the item to open, like so: '.inventory open ROW,COLUMN'\nFor example, to open the first item in your inventory, you would use '.inventory open 1,1'")
            return
        requested_slot = split_msg[2]
        # Ensure row/column are valid
        if not requested_slot.isdigit() or int(requested_slot) > 250 or int(requested_slot) <= 0:
            await message.channel.send("That inventory slot is empty!")
            return
        # Figure out what item to look up
        item_instance = await inventory.get_item_in_slot(cursor, follower_info["id"], requested_slot)
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
        await inventory.delete_item(cursor, follower_info["id"], requested_slot)
        # Delete item instance
        await item.delete_item(cursor, item_instance["item_id"])
        return


async def handle_material(message, deity_info, follower_info):
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


async def handle_message_from_deity(message, deity_info):
    body = message.content.lower() + " "
    follower_info = await follower.get_follower_info_by_deity(cursor, deity_info["id"])
    if body.startswith(".h ") or body.startswith(".help "):
        await message.channel.send("Welcome to Project Deity! You can view the commands here:\n<https://github.com/Frostflake/project-deity/wiki/Discord-Commands>")
    elif body.startswith(".r ") or body.startswith(".register "):
        await message.channel.send("You are already registered!")
    elif body.startswith(".f ") or body.startswith(".follower "):
        await handle_follower(message, deity_info, follower_info)
    elif body.startswith(".d ") or body.startswith(".daily "):
        await handle_daily(message, deity_info, follower_info)
    elif body.startswith(".s ") or body.startswith(".stats "):
        await handle_stats(message, deity_info, follower_info)
    elif body.startswith(".l ") or body.startswith(".lexicon "):
        await handle_lexicon(message)
    elif body.startswith(".i ") or body.startswith(".inventory "):
        await handle_inventory(message, deity_info, follower_info)
    elif body.startswith(".c ") or body.startswith(".craft "):
        await handle_craft(message, deity_info, follower_info)
    elif body.startswith(".m ") or body.startswith(".mat "):
        await handle_material(message, deity_info, follower_info)


async def handle_message_from_nondeity(message):
    body = message.content.lower() + " "
    if body.startswith(".h ") or body.startswith(".help "):
        await message.channel.send("Welcome to Project Deity! You can view the commands here:\n<https://github.com/Frostflake/project-deity/wiki/Discord-Commands>")
    elif body.startswith(".r ") or body.startswith(".register "):
        await handle_registration(message)
    elif body.startswith(".l ") or body.startswith(".lexicon "):
        await handle_lexicon(message)


async def handle_admin_command(message):
    split_msg = [x.strip() for x in message.content.split("::")]
    if split_msg[1] == "additem":
        if len(split_msg) != 4:
            await message.channel.send(".admin::additem::follower_id::item_id")
            return
        item_instance_id = await item.create_item_instance(cursor, int(split_msg[3]))
        if not item_instance_id:
            await message.channel.send("Item instance generation failed.")
            return
        add_item_success = await inventory.add_item(cursor, int(split_msg[2]), item_instance_id)
        if not add_item_success:
            # Clean up item instance
            await item.delete_item(cursor, item_instance_id)
            await message.channel.send("Item could not be added to inventory.")
        else:
            await message.channel.send("Item added to inventory.")
    if split_msg[1] == "custom":
        # channel = client.get_channel(763139386983710730)
        pass


@client.event
async def on_message(message):
    # Skip self messages and non-commands
    if message.author.id == client.user.id or not message.content.startswith("."):
        return
    if message.content.startswith(".admin") and message.author.id == config["discord"]["admin"]:
        await handle_admin_command(message)
    # Get deity and follower info
    deity_info = await deity.get_deity_by_discord(cursor, message.author.id)
    if deity_info is not None:
        await handle_message_from_deity(message, deity_info)
    else:
        await handle_message_from_nondeity(message)

if os.path.isfile("discord.token"):
    with open("discord.token") as file:
        token = file.read()
else:
    with open("discord.token", 'w') as file:
        token = input("Please give me the token for the Discord bot: ")
        token = token.strip()
        file.write(token)

client.run(token)
