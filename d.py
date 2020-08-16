"""
This module contains an autoresponder for Discord.
Based on discord.py package, have to be run in a subprocess.
"""

import argparse
import os
import sys

import aiohttp
import discord
from dotenv import load_dotenv

import rureply

load_dotenv()

d_client = discord.Client(proxy_auth=aiohttp.BasicAuth(login=os.getenv('D_EMAIL'), password=os.getenv('D_PASS')))

d_replied = set()


@d_client.event
async def on_message(message):
    free_in = rureply.get_remaining_seconds(args.time)
    # The check in case the main process stops without closure this subprocess.
    if free_in <= 0:
        sys.exit(0)
    else:
        sender = message.author.id
        # Send only one auto-reply per user.
        if sender not in d_replied:
            if msg := rureply.get_d_message(free_in):
                d_replied.add(sender)
                await message.channel.send(msg)


parser = argparse.ArgumentParser()
parser.add_argument('time', type=str)
args = parser.parse_args()

d_client.run(os.getenv('D_TOKEN'), bot=False)
