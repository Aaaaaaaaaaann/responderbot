import os


def get_tg_ids():
    with open(f'{os.path.dirname(os.path.abspath(__file__))}/tg_users.txt', 'r') as file:
        return {int(id) for id in file.read().split()}


ME = ...
LENA = ...
