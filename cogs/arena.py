from discord.ext import commands
from cogs.utils.event import Event, Guide, MessageListener


def format_event(i, event: Event):
    return f"ID:{i+1:2}\tHora: {event.date.strftime('%H:%M')}\tDeporte: {event.sport:17}Partido: {event.name}\n"


class Arena:
    def __init__(self, bot):
        self.bot = bot
        self.guide = Guide.get_instance()
        self.message_listener = MessageListener.get_instance()

    async def add_emojis(self, nums, msg):
        for x in range(nums):
            await msg.add_reaction(self.message_listener.emojis.get(str(x+1)))
        await msg.add_reaction(self.message_listener.emojis.get("left"))
        await msg.add_reaction(self.message_listener.emojis.get("right"))
        await msg.add_reaction(self.message_listener.emojis.get("delete"))

    @commands.command(name="ace")
    async def ace(self, ctx, order):
        if order == "list":
            msg = await ctx.send(f"DESCARGANDO LOS ÚLTIMOS EVENTOS DEPORTIVOS")
            events = self.guide.get_all_events()
            events = self.message_listener.add_events(msg.guild.id, msg.id, events)
            page, page_total = self.message_listener.get_page(msg.guild.id, msg.id)
            text = f"Lista de eventos [Página {page} de {page_total}]:\n"
            for i, event in enumerate(events):
                text += format_event(i, event)
            await msg.edit(content=f"```{text}```")
            await self.add_emojis(self.message_listener.events_per_page, msg)
        if order == "update":
            msg = await ctx.send("Actualizando eventos deportivos")
            self.guide.scrape_events()
            await msg.edit("Eventos actualizados")


def setup(bot):
    bot.add_cog(Arena(bot))
