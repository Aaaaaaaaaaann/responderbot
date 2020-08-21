"""
This module is for evaluating and converting time to less accurate but more human-understandable format:
1. An hour is divided into three intervals of 20 minutes.
2. Based on the interval the module builds a string with the remaining time.
3. The string is put to the message.
This formatting makes it unnecessary for your interlocutors to count themselves how long it takes you to return.
The module helps build messages only if the user is out for a few hours, but not days.
"""

from datetime import datetime

# 01: 0 h, 0 <= min <= 19; -> None
# 02: 0 h, 20 <= min <= 39
# 03: 0 h, 40 <= min <= 59
# 11: 1 h, 0 <= min <= 19
# 12: 1 h, 20 <= min <= 39; -> 2 h
# 13: 1 h, 40 <= min <= 59
# 1: 2 <= h <= 4, 0 <= min <= 19
# 2: 2 <= h <= 4, 20 <= min <= 39

TIME = {
    '01': None,
    '02': 'half an hour',
    '03': 'an hour',
    '11': 'an hour',
    '12': 'an hour and a half',
    '13': 'two hours',
    '1': ' hours',
    '2': ' hours and a half'
}

HOURS = {
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven'
}


def get_message(seconds):
    """Return the message with the remaining time for Telegram users."""
    time = get_human_time(seconds)
    if time:
        return f'Hello! I am busy right now and I will get back to work in {time}, sorry.\n\n' \
               f'If it is something urgent, write {...}, please.\n\n' \
               'Or wait for me if you can. I will take on your task as soon as I am free.'


def get_remaining_seconds(str_time):
    """Return the remaining time in seconds."""
    current_time = datetime.utcnow().strftime('%H:%M')
    # 10_800 - the difference in seconds from Moscow (3 hours)
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
    elif hours >= 2:
        if m == '3':
            return f'{HOURS[hours+1]}{TIME["1"]}'
        return f'{HOURS[hours]}{TIME[m]}'
    return TIME[f'{h}{m}']
