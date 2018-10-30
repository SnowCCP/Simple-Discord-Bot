from discord.ext import commands
from cogs.utils import config
import configparser
import asyncio
import os

description = '''Bot que hace cosas y tal.

Quizá algún día llegue a ser útil.'''

# Extensions to loads
startup_extensions = ["cogs.admin"]

bot = commands.Bot(command_prefix="$", description=description)
config_json = config.Config("config.json")


async def check_forbidden_prefixes(message):
    prefixes = config_json.get_forbidden_prefix(str(message.guild.id))
    for prefix in prefixes:
        if message.content.startswith(prefix["prefix"]):
            if message.channel.id not in prefix["allowed_channels"]:
                await message.delete()
                tmp = await message.channel.send(prefix["warning_message"])
                if prefix["time"] is not None:
                    await asyncio.sleep(prefix["time"])
                    await tmp.delete()
                return True
    return False


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
    if await check_forbidden_prefixes(message):
        return
    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    await config_json.add_guild(str(guild.id))

if __name__ == "__main__":
    try:
        configuration = configparser.ConfigParser()
        configuration.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
        token = configuration["Credentials"]["Token"]
    except Exception as e:
        print('Failed to load config.ini')
        exit()

    for extension in startup_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

    bot.run(token, bot=True, reconnect=True)
