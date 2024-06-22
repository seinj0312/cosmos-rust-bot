#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from asyncio import sleep as asleep

import discord
import requests
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.realpath(__file__))
if not os.path.isfile(os.path.join(current_dir, ".env")):
    print(
        "No .env file found, make sure to copy .env.example to .env and fill in the values"
    )
    exit(1)

load_dotenv()
SYMBOL = os.getenv("PRICEBOT_SYMBOL", "")
guildID = int(os.getenv("PRICEBOT_GUILD_ID", 0))
memberID = int(os.getenv("PRICEBOT_MEMBER_ID", 0))
BOT_TOKEN = os.getenv("PRICEBOT_BOT_TOKEN", "")

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def getOsmosisPrice():
    headers = {"Host": "api-osmosis.imperator.co", "Accept": "*/*"}
    a = requests.get(
        f"https://api-osmosis.imperator.co/tokens/v2/{SYMBOL}",
        headers=headers,
        timeout=20,
    )
    if a.status_code == 200:
        z = round(json.loads(a.text)[0]["price"], 2)
        y = round(json.loads(a.text)[0]["price_24h_change"], 2)
        if z == None:
            getOsmosisPrice()
        else:
            return z, y
    else:
        getOsmosisPrice()


@client.event
async def on_ready():
    print(f"You have logged in as {client}")
    guild = client.get_guild(guildID)
    member = guild.get_member(memberID)
    while True:
        try:
            price, PriceChange = getOsmosisPrice()
            await member.edit(nick=f"{SYMBOL} ${price}")
            await asleep(1)

            if PriceChange > 0:
                PriceChange = "+" + str(PriceChange)
                
            await client.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name="Δ 24h: " + str(PriceChange) + "%",
                )
            )

            await asleep(28)
        except:
            continue


client.run(BOT_TOKEN)
