from discord.ext import commands


class Admin:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, *args):
        await self.bot.say('{} arguments: {}'.format(len(args), ', '.join(args)))


def setup(bot):
    bot.add_cog(Admin(bot))
