# ResponderBot
This is a personal Telegram bot, which you can use to write your one.
## What does it do
The bot is needed to reply to my colleagues when I am not available. It performs four functions:
1. Runs two auto-responders: one for Telegram and one for Discord.
2. Stops auto-responders.
3. Adds IDs of Telegram users to the set of recipients.
4. Removes IDs from this set.

## How does it work
The bot consists of the main module, two subprograms, and three supportive modules.
### `main.py`
The main module is written using [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI). It responds all correct requests to the bot and manages the two subprograms: run and kill them on request and also kill subprograms if the time they have to work has passed.
### `tg.py` and `d.py`
These are subprograms that send replies in Telegram and Discord respectively. They are run by `main.py` in subprocesses using the Python subprocess module. In the case the `main.py` is stopped because of an unforeseen error they can finish their work themselves: there are time checks for this.

To run these modules a user of the bot has to specify when he will be available again.
### `rureply.py` and `enreply.py`
These modules summarize time, for example: if there are 48 minutes before auto-responders will be stopped, the module converts it in 'an hour'. The first module is for Russian, and the second one is for English.

The modules include two dictionaries to build a string: the first one with different strings with 'an hour' and 'a half' and the second one with string numbers. It works so:
1. If a new message is got, a responder calls a function from a module.
2. The module counts in what time the responders will be stopped.
3. Then the module converts the time in a string, puts it in a massage, and returns this message.
#### `users.py`
It contains variables with IDs of Telegram users. The recipients are stored in a set, which may be changed by a bot user.
#### `smtplog.py`
It merely contains an overridden omit() method of a class SMTPHandler from the logging package. This was needed for proper sending emails with tracebacks.
## How can you use it
If the functionality of this bot suits your usage scenarios, there is not much to do.

Create a project:

    git clone https://github.com/Aaaaaaaaaaann/responderbot.git
    cd responderbot
    python3 -m venv
    pip install -r requirements.txt

[Create](https://core.telegram.org/bots#6-botfather) a bot.

Write a message (or messages) using `enreply.py` or `rureply.py` (or rewrite the dictionaries and get_human_time() to be applicable to your language). Or, probably, you may come up with a better and more beautiful idea (hopefully, you will).

In the same module, put the difference between your time zone and UTC in seconds (the last value):

    # 10_800 - the difference in seconds from Moscow (3 hours)
    return (datetime.strptime(str_time, '%H:%M') - datetime.strptime(current_time, '%H:%M')).seconds - 10_800

Create a module for auto-replies in Telegram. It can be written using [Telethon](https://docs.telethon.dev/en/latest/) library like in this project. If you use Telethon, run your alternative of `tg.py` firstly to authorize and create a `.session` file. Don't delete your `.session` file and don't use it somewhere else while your `tg.py` is being run.

Create similar modules for any messengers you need. For example, in this project [discord.py](https://discordpy.readthedocs.io/en/latest/) was used for Discord.

Create Popen objects for your auto-responders instead of current ones:

    def run_subprocs(free_at):
    """Run subprocesses, save their PIDs and run errors listeners."""
        tg_subproc = subprocess.Popen([f'{wrkdir}/venv/bin/python', f'{wrkdir}/tg.py', free_at], stderr=subprocess.PIPE)
        d_subproc = subprocess.Popen([f'{wrkdir}/venv/bin/python', f'{wrkdir}/d.py', free_at], stderr=subprocess.PIPE)
        subprocs = [tg_subproc, d_subproc]

If it isn't what you were looking for, anyway, you probably can find the techniques here that might come in handy to write your bot.
