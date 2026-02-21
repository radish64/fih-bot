#!/usr/bin/env python3

import discord
from discord import app_commands

import fishy
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


@tree.command(name = 'fish', description = 'Catch fishies!')
async def fish_command(interaction):
    user = interaction.user
    #print(f"{user.id} {user.name}, {user.global_name}, {user.display_name}")
    lastFishedTime = fishy.check_timestamp(user)
    if(int(datetime.now().timestamp() - lastFishedTime > 3600)):
        fih = fishy.catch_fish(user)
        caughtFishy = fih[0]
        caughtFishies = fih[1] 
        if caughtFishies == 100:
            caughtFishies = "💯";
        await interaction.response.send_message(f"Caught a{str(caughtFishy)} worth {str(caughtFishies)} fih!")
        print(f"Caught {str(caughtFishies)} for {user}")
    else:
        waitTime = 3600 - (int(datetime.now().timestamp()) - lastFishedTime)
        await interaction.response.send_message(errors[random.randint(0,len(errors)-1)])
        #await interaction.response.send_message("Wait " + str(waitTime // 3600) + " hours, " + str(waitTime % 3600 // 60) + " minutes, " + str(waitTime % 3600 % 60) + " seconds :3")
        print(int(datetime.now().timestamp()) - lastFishedTime)

@tree.command(name = 'leaderboard', description = 'Show fishy leaderboard')
async def leaderboard_command(interaction):
    table = fishy.print_db().getvalue()
    await interaction.response.send_message(table)
	

@client.event
async def on_ready():
	await client.wait_until_ready()
	print(f'We have logged in as {client.user}')
	await tree.sync()


client.run(bot_key)
