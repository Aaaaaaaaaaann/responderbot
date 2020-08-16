"""
This module contains an autoresponder for Telegram.
Based on Telethon package, have to be run in a subprocess.
"""

import argparse
import os
import sys

from dotenv import load_dotenv
import telethon

import users
import rureply

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('time', type=str)
args = parser.parse_args()


API_ID = os.getenv('TG_ID')
API_HASH = os.getenv('TG_HASH')
tg_client = telethon.TelegramClient(f'{os.path.dirname(os.path.abspath(__file__))}/my', API_ID, API_HASH)

tg_replied = set()


@tg_client.on(telethon.events.NewMessage(incoming=True, func=lambda x: x.is_private,
                                         from_users=(users.get_tg_ids() - tg_replied)))
async def message_handler(event):
    free_in = rureply.get_remaining_seconds(args.time)
    # The check in case the main process stops without closure this subprocess.
    if free_in <= 0:
        sys.exit(0)
    else:
        sender = await event.get_sender()
        if msg := rureply.get_tg_message(free_in):
            await event.client.send_message(sender.id, msg)
            await tg_client.send_message('me', f'Write {sender.first_name} {sender.last_name}.')
            tg_replied.add(sender.id)


tg_client.start()
tg_client.run_until_disconnected()
