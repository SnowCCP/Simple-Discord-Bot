from discord.ext import commands
from cogs.utils import config, event
import configparser
import asyncio
import os

description = '''Bot que hace cosas y tal.

Quizá algún día llegue a ser útil.'''

# Extensions to loads
startup_extensions = ["cogs.admin", "cogs.arena"]

bot = commands.Bot(command_prefix="$", description=description)
config_json = config.ConfigPrefix("config/config_prefix.json")
message_listener = event.MessageListener.get_instance()
guide = event.Guide.get_instance()


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


async def update_events(msg):
    events = message_listener.get_events(msg.guild.id, msg.id)
    page, page_total = message_listener.get_page(msg.guild.id, msg.id)
    text = f"Lista de eventos [Página {page} de {page_total}]:\n"
    for i, entry in enumerate(events):
        text += f"ID:{i+1:2}\tHora: {entry.date.strftime('%H:%M')}\tDeporte: {entry.sport:17}Partido: {entry.name}\n"
    await msg.edit(content=f"```{text}```")


async def send_channel_links(reaction):
    number = None
    for k, v in message_listener.emojis_number.items():
        if reaction.emoji == v:
            number = int(k)
    uuid = message_listener.get_uuid_event(reaction.message.guild.id, reaction.message.id, number)
    if uuid is None:
        return None
    # TODO: mirar si ya se tienen los enlaces
    entry = guide.get_links_by_uuid(uuid)
    if entry is None:
        return None

    message_listener.delete_message(reaction.message.guild.id, reaction.message.id)
    await reaction.message.delete()

    text = f"Enlaces al partido {entry.name}:\n"
    for channel in entry.channels:
        text += f"Canal: {channel.number}\tIdioma: {channel.language}\tEnlace: {channel.link}\n"

    channel_send = bot.get_channel(reaction.message.channel.id)
    await channel_send.send(f"```{text}```")
    return True

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return
    if message_listener.is_message_on_listener(reaction.message.guild.id, reaction.message.id):
        if reaction.emoji in message_listener.emojis.values():
            if reaction.emoji in message_listener.emojis.get("delete"):
                await reaction.message.delete()
                message_listener.delete_message(reaction.message.guild.id, reaction.message.id)
                return
            if reaction.emoji in message_listener.emojis.get("left"):
                if message_listener.has_previous_page(reaction.message.guild.id, reaction.message.id):
                    await update_events(reaction.message)
            if reaction.emoji in message_listener.emojis.get("right"):
                if message_listener.has_next_page(reaction.message.guild.id, reaction.message.id):
                    await update_events(reaction.message)
            if reaction.emoji in message_listener.emojis_number.values():
                response = await send_channel_links(reaction)
                if response is not None:
                    return
            await reaction.message.remove_reaction(reaction.emoji, user)
        else:
            await reaction.message.remove_reaction(reaction.emoji, user)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #if await check_forbidden_prefixes(message):
    #    return
    await bot.process_commands(message)


@bot.event
async def on_guild_join(guild):
    await config_json.add_guild(str(guild.id))

if __name__ == "__main__":
    try:
        configuration = configparser.ConfigParser()
        configuration.read(os.path.join(os.path.dirname(__file__), 'config/config.ini'))
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
