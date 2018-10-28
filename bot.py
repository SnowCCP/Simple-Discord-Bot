from discord.ext import commands
import configparser
import discord
import os

description = '''Bot que hace cosas y tal.

Quizá algún día llegue a ser útil.'''

# Extensions to loads
startup_extensions = ["cogs.admin"]

bot = bot = commands.Bot(command_prefix='$', description=description)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return


if __name__ == "__main__":
    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))
    try:
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    except Exception as e:
        print('Failed to load config.ini')
        exit()

    bot.run(config["Credentials"])
