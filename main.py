"""The main module for bot managing and running subprocesses with autoresponders.
Based on pyTelegramBotAPI.
"""

from datetime import datetime
import logging
import os
import re
from signal import SIGINT
import subprocess
import threading
import time

from dotenv import load_dotenv
import telebot

import rureply
from smtplog import MySMTPHandler
import users

load_dotenv()

log_handler = MySMTPHandler(mailhost=('smtp.gmail.com', 587), fromaddr=os.getenv('LOG_EMAIL'),
                            toaddrs=[os.getenv('LOG_EMAIL')], subject='Responderbot error',
                            credentials=(os.getenv('LOG_EMAIL'), os.getenv('LOG_PASS')))
logging.basicConfig(format='[%(levelname) 5s | %(asctime)s] %(funcName)s: %(message)s',
                    level=logging.WARNING, handlers=[log_handler])

# ************* Subprocesses' handlers ************* #

wrkdir = os.path.dirname(os.path.abspath(__file__))

pids = []
run = False


def catch_subproc_err(subproc):
    """Being run in a separate thread listen to errors in the subprocesses."""
    try:
        _, errs = subproc.communicate()
        if errs:
            logging.error(errs)
    except subprocess.SubprocessError as e:
        logging.error(e)


def run_subprocs(free_at):
    """Run subprocesses, save their PIDs and run errors listeners."""
    tg_subproc = subprocess.Popen([f'{wrkdir}/venv/bin/python', f'{wrkdir}/tg.py', free_at], stderr=subprocess.PIPE)
    d_subproc = subprocess.Popen([f'{wrkdir}/venv/bin/python', f'{wrkdir}/d.py', free_at], stderr=subprocess.PIPE)
    subprocs = [tg_subproc, d_subproc]

    global pids, run
    pids += [subproc.pid for subproc in subprocs]
    run = True

    for subproc in subprocs:
        subproc_communicate = threading.Thread(target=catch_subproc_err, args=(subproc,))
        subproc_communicate.start()
    autostop = threading.Thread(target=autostop_subprocs, args=(free_at,))
    autostop.start()


def stop_subprocs():
    """Send SIGINT to the subprocesses."""
    global pids, run
    try:
        for pid in pids:
            os.kill(pid, SIGINT)
    except ProcessLookupError as e:
        logging.error(e)
    finally:
        run = False
        pids.clear()


def autostop_subprocs(free_at):
    """Wait and stop subrocesses, if the user doesn't do this."""
    timeout = rureply.get_remaining_seconds(free_at)
    time.sleep(timeout)
    global run
    if run:
        stop_subprocs()
        notify_of_finish()


# ******************** Helpers ******************** #

def is_me(func):
    def inner(*args):
        if args[0].chat.id == users.ME:
            return func(*args)
    return inner


def is_cancel(func):
    def inner(*args):
        if args[0].text == '/cancel':
            bot.send_message(args[0].chat.id, 'Cancelled.')
            return
        return func(*args)
    return inner


def build_btn(*btn_names):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = []
    for name in btn_names:
        btn = telebot.types.KeyboardButton(name)
        btns.append(btn)
    markup.row(*btns)
    return markup


# ********************** Bot ********************** #

bot = telebot.TeleBot(os.getenv('TG_TOKEN'))


@is_me
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, 'Let\'s run responders.', reply_markup=build_btn('Run'))


@is_cancel
def run_responders(message):
    free_at = message.text
    if re.match(r'([0-1]\d|2[0-3]):[0-5]\d', free_at):
        if free_at > datetime.now().strftime('%H:%M'):
            run_subprocs(free_at)
            bot.send_message(message.chat.id, 'Run.', reply_markup=build_btn('Stop'))
        else:
            bot.send_message(message.chat.id, 'Press "Run" again and send me correct time.',
                             reply_markup=build_btn('Run'))
    else:
        bot.send_message(message.chat.id, 'Press "Run" again and send me correct time.',
                         reply_markup=build_btn('Run'))


@is_me
@bot.message_handler(func=lambda message: message.text == 'Run')
def ask_time(message):
    bot.send_message(message.chat.id, 'What time will you be available? (Format: 00:00.)',
                     reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, run_responders)


def notify_of_finish():
    bot.send_message(users.ME, 'Responders have been disconnected.', reply_markup=build_btn('Run'))


@is_me
@bot.message_handler(func=lambda message: message.text == 'Stop')
def stop_handle(message):
    if run:
        stop_subprocs()
        notify_of_finish()


@is_me
@bot.message_handler(commands=['users'])
def users_handle(message):
    bot.send_message(users.ME, 'Choose an action.', reply_markup=build_btn('Add', 'Delete'))


def add_user(message):
    id = int(message.text)
    if id in users.tg_users:
        bot.send_message(message.chat.id, 'The ID is already on the list.')
    else:
        users.tg_users.add(id)
        bot.send_message(message.chat.id, 'The ID is on the list.')


@is_cancel
def get_id(message, action_handler):
    if message.text.isnumeric() and len(message.text) == 9:
        action_handler(message)
    else:
        bot.send_message(message.chat.id, 'Choose an action again and send me a correct ID.',
                         reply_markup=build_btn('Add', 'Delete'))


def delete_user(message):
    try:
        users.tg_users.remove(int(message.text))
    except KeyError:
        bot.send_message(message.chat.id, 'There is not such ID on the list.')
    else:
        bot.send_message(message.chat.id, 'The ID is no longer on the list.')


@is_me
@bot.message_handler(func=lambda message: message.text == 'Add')
def add_handle(message):
    bot.send_message(message.chat.id, 'Send me an ID.', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_id, add_user)


@is_me
@bot.message_handler(func=lambda message: message.text == 'Delete')
def delete_handle(message):
    bot.send_message(message.chat.id, 'Send me an ID.', reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_id, delete_user)


bot.polling()
