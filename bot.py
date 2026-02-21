#!/usr/bin/env python3

import discord
from discord import app_commands

import fishy
import shop
from datetime import datetime

import io
import re
import random
from fihfile import fihfile

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

tree = app_commands.CommandTree(client)

bot_key = "YOUR BOT KEY"

errors = fihfile("errors.fih").getCategory("Errors")


@tree.command(name = 'fish', description = 'catch fishies!')
async def fish_command(interaction):
    user = interaction.user
    #print(f"{user.id} {user.name}, {user.global_name}, {user.display_name}")
    lastfishedtime = fishy.check_timestamp(user)
    if(int(datetime.now().timestamp() - lastfishedtime > 3600)):
        fih = fishy.catch_fish(user)
        caughtfishy = fih[0]
        caughtfishies = fih[1] 
        if caughtfishies == 100:
            caughtfishies = "💯";
        await interaction.response.send_message(f"caught a{str(caughtfishy)} worth {str(caughtfishies)} fih!")
        print(f"caught {str(caughtfishies)} for {user}")
    else:
        waittime = 3600 - (int(datetime.now().timestamp()) - lastfishedtime)
        await interaction.response.send_message(errors[random.randint(0,len(errors)-1)])
        #await interaction.response.send_message("wait " + str(waittime // 3600) + " hours, " + str(waittime % 3600 // 60) + " minutes, " + str(waittime % 3600 % 60) + " seconds :3")
        print(int(datetime.now().timestamp()) - lastfishedtime)

@tree.command(name = 'leaderboard', description = 'show fishy leaderboard')
async def leaderboard_command(interaction):
    table = fishy.print_db().getvalue()
    await interaction.response.send_message(table)

@tree.command(name = 'shop', description = 'show fishy shop')
async def shop_command(interaction):
    table = shop.print_shop()
    await interaction.response.send_message(table)

@tree.command(name = 'items', description = 'show your items')
async def items_command(interaction):
    table = shop.print_inventory(interaction.user)
    await interaction.response.send_message(table)

@tree.command(name = 'buy', description = 'buy an item with fih points!')
async def buy_command(interaction, item: str):
    user = interaction.user
    purchase=shop.buy_item(user,item)
    message=""
    if (purchase == 1):
        message = "Are you stupid? That's not an item"
    elif (purchase == 2):
        message = "Who are you???"
    elif (purchase == 3):
        message = "IT SMELLS LIKE BROKE IN HERE!"
    else:
        message = f"Enjoy your {purchase}!"
    await interaction.response.send_message(message)
	
@client.event
async def on_ready():
	await client.wait_until_ready()
	print(f'We have logged in as {client.user}')
	await tree.sync()


client.run(bot_key)
