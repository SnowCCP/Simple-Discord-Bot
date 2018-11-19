from discord.ext import commands
from cogs.utils import config


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.config_json = config.ConfigPrefix("config.json")

    @commands.command(name="test")
    async def test(self, ctx, *args):
        await ctx.send('{} arguments: {}'.format(len(args), ', '.join(args)))

    @commands.command(name="prefix")
    async def prefix(self, ctx, order, *argv):
        if order == "list":
            prefixes = self.config_json.get_forbidden_prefix(str(ctx.message.guild.id))
            msg = "Listado de prohibiciones:\n```\n"
            for idx, prefix in enumerate(prefixes):
                msg += f"{idx}) Prefijo: {prefix['prefix']}\tCanales permitidos: {prefix['allowed_channels']}\tTiempo borrado: {prefix['time']}s\tMensaje:{prefix['warning_message']}\n"
            msg += "```"
            await ctx.send(msg)
        if order == "add":
            if len(argv) < 4:
                await ctx.send('ERROR: Utiliza prefix add "prefijo" "mesaje a mostrar" segundos ID_CANAL_PERMITIDO1 ID_CANAL_PERMITIDO2 ...')
                return
            dic = dict()
            dic["prefix"] = str(argv[0])
            dic["warning_message"] = str(argv[1])
            dic["time"] = int(argv[2])
            dic["allowed_channels"] = [int(x) for x in argv[3:]]
            await self.config_json.add_forbidden_prefix(str(ctx.message.guild.id), dic)
            await ctx.send("Prohibición añadida")


def setup(bot):
    bot.add_cog(Admin(bot))
