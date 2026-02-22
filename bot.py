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

async def go_fish(interaction, modifier):
    user = interaction.user
    lastfishedtime = fishy.check_timestamp(user)
    if(int(datetime.now().timestamp() - lastfishedtime > 3600)):
        if shop.hasGoldenRod(user):
            modifier += 100
        fih = fishy.catch_fish(user,modifier)
        caughtfishy = fih[0]
        caughtfishies = fih[1] 
        if caughtfishies == 100:
            caughtfishies = "💯";
        await interaction.response.send_message(f"Caught a{str(caughtfishy)} worth {str(caughtfishies)} fih!")
        print(f"Caught {str(caughtfishies)} for {user}")
        return 1
    else:
        waittime = 3600 - (int(datetime.now().timestamp()) - lastfishedtime)
        await interaction.response.send_message(errors[random.randint(0,len(errors)-1)])
        print(int(datetime.now().timestamp()) - lastfishedtime)
        return 0


@tree.command(name = 'fish', description = 'catch fishies!')
async def fish_command(interaction):
    await go_fish(interaction,0)

@tree.command(name = 'leaderboard', description = 'show fishy leaderboard')
async def leaderboard_command(interaction):
    table = fishy.print_db()
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

class items(Enum):
    WORM=1
    LURE=2
    BARNACLE=3
    TOY=4
    GOLDEN=5
    BOMB=6
    CHILIS=7

@tree.command(name = 'use', description = 'buy an item with fih points!')
async def use_command(interaction, item: str, target: str=None):
    user = interaction.user
    result=shop.use_item(user,item)
    print(result)
    message=""
    if (result == -1):
        message="Are you stupid? That's not an item"
    elif (result == -2):
        message="Are you stupid? You don't have that item"
    elif (result[1] == items.WORM.value):
        fished = await go_fish(interaction,50)
        if (fished):
            shop.delete_item(result[0])
        return 0
    elif (result[1] == items.LURE.value):
        fished = await go_fish(interaction,100)
        if (fished):
            shop.delete_item(result[0])
        return 0
    elif (result[1] == items.BARNACLE.value):
        if (not target):
            message = "Ping a user to attack!"
        else:
            fishy.destroy_fish((re.split('<|@|>',target)[2]),100)
            message=f"Barnacles destroyed 100 of {target}'s fih!"
            shop.delete_item(result[0])
    elif (result[1] == items.TOY.value):
        river_uid = 346826648865210368
        message=f"<@{river_uid}> {user.display_name} has ordered a toy!"
    elif (result[1] == items.GOLDEN.value):
        message="Use `/fish` to use the Golden Rod"
    elif (result[1] == items.BOMB.value):
        users = fishy.getAllUsers()
        for user in users:
            fishy.destroy_fish(user,100)
        message="BOMB THEM!"
        shop.delete_item(result[0])
    elif (result[1] == items.CHILIS.value):
        river_uid = 346826648865210368
        message=f"<@{river_uid}> Chili's awaits you..."
    else:
        message="You can't use that item!"
    await interaction.response.send_message(message)

	
@client.event
async def on_ready():
	await client.wait_until_ready()
	print(f'We have logged in as {client.user}')
	await tree.sync()


client.run(bot_key)
