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
SYMBOL = os.getenv("WYNDBOT_SYMBOL", "")
WYNDBOT_HUMAN_SYMBOL = os.getenv("WYNDBOT_HUMAN_SYMBOL", "")
guildID = int(os.getenv("WYNDBOT_GUILD_ID", 0))
memberID = int(os.getenv("WYNDBOT_MEMBER_ID", 0))
BOT_TOKEN = os.getenv("WYNDBOT_BOT_TOKEN", "")

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def getChange() -> float:
    print(f"Getting {SYMBOL} Price Change")

    a = requests.get(f"https://api.wynddao.com/assets/prices/historical/{SYMBOL}", timeout=20)
    if a.status_code == 200:
        values = a.json()
        first = values[0]
        last = values[-1]

        firstPrice = first["priceInUsd"]
        lastPrice = last["priceInUsd"]

        change = round((lastPrice - firstPrice) / firstPrice * 100, 2)

        return change
    else:
        getChange()        

def getWyndPrice():
    headers = {"Host": "api.wynddao.com", "Accept": "*/*"}
    print(f"Getting {SYMBOL} Price")
    a = requests.get(
        f"https://api.wynddao.com/assets/prices",
        headers=headers,
        timeout=20,
    )
    if a.status_code == 200:
        asset: dict
        for asset in list(a.json()):
            if asset.get("asset", "") == SYMBOL:
                return asset["priceInUsd"]
    else:
        getWyndPrice()


@client.event
async def on_ready():
    print(f"You have logged in as {client}")
    guild = client.get_guild(guildID)
    member = guild.get_member(memberID)
    while True:
        try:
            price, PriceChange = getWyndPrice(), getChange()

            await member.edit(nick=f"{WYNDBOT_HUMAN_SYMBOL} ${price:,.3f}")
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
