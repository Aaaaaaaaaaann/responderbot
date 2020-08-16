"""
This module is for evaluating and converting time to less accurate but more human-understandable format:
1. An hour is divided into three intervals of 20 minutes.
2. Based on the interval the module builds a string with the remaining time.
3. The string is put to the message.
This formatting makes it unnecessary for your interlocutors to count themselves how long it takes you to return.
The module helps build messages only if the user is out for a few hours, but not days.
Use it for sending messages in Russian.
enreply.py - an alternative for messages in English.
"""

from datetime import datetime

import users

# 01: 0 h, 0 <= min <= 19; -> None
# 02: 0 h, 20 <= min <= 39
# 03: 0 h, 40 <= min <= 59
# 11: 1 h, 0 <= min <= 19
# 12: 1 h, 20 <= min <= 39; -> 2 h
# 13: 1 h, 40 <= min <= 59
# 1: 2 <= h <= 4, 0 <= min <= 19
# 2: 2 <= h <= 4, 20 <= min <= 39
# 3, 4: h >= 4, 20 <= min <= 39; -> N + 1 h

TIME = {
    '01': None,
    '02': 'полчаса',
    '03': 'час',
    '11': 'час',
    '12': 'полтора часа',
    '13': 'два часа',
    '1': ' часа',
    '2': ' с половиной часа',
    '3': ' часов'
}

HOURS = {
    2: 'два',
    3: 'три',
    4: 'четыре',
    5: 'пять',
    6: 'шесть',
    7: 'семь'
}


def get_tg_message(seconds):
    """Return the message with the remaining time for Telegram users."""
    time = get_human_time(seconds)
    if time:
        return f'Привет, я сейчас занята и смогу взяться за задачу примерно через {time}.\n\n' \
               f'Если нужно проверить текст быстрее или уточнить что-то по грамматике, то напиши, ' \
               f'пожалуйста, Лене, другому корректору: {users.LENA}.\n\n' \
               'Если можешь подождать, то напиши мне «жду» – я примусь за твою задачу, как только освобожусь.'


def get_d_message(seconds):
    """Return the message with the remaining time for Discord users."""
    time = get_human_time(seconds)
    if time:
        return f'Привет, я сейчас занята и освобожусь примерно через {time}.\n' \
               'Если это срочно, то напиши, пожалуйста, Лене.'


def get_remaining_seconds(str_time):
    """Return the remaining time in seconds."""
    current_time = datetime.utcnow().strftime('%H:%M')
    # 10_800 - the difference in seconds from my region (3 hours)
    return (datetime.strptime(str_time, '%H:%M') - datetime.strptime(current_time, '%H:%M')).seconds - 10_800


def get_human_time(seconds):
    """Count how long it will take you before coming back."""
    hours = seconds // 3660
    minutes = (seconds // 60) % 60
    if minutes <= 19:
        m = '1'
    elif 20 <= minutes <= 39:
        m = '2'
    elif minutes >= 40:
        m = '3'
    if not hours:
        h = '0'
    elif hours == 1:
        h = '1'
    elif 2 <= hours < 4:
        if m == '3':
            return f'{HOURS[hours+1]}{TIME["1"]}'
        return f'{HOURS[hours]}{TIME[m]}'
    elif hours >= 4:
        return f'{HOURS[hours+1]}{TIME["3"]}'
    return TIME[f'{h}{m}']
