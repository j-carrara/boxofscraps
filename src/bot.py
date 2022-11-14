import discord
from discord.ext import commands
import logging
from config import DISCORD_TOKEN, COMMAND_PREFIX
from commands import MusicCommands

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents= discord.Intents.all())

@bot.event
async def on_ready():
    await bot.add_cog(MusicCommands(bot))
    await bot.tree.sync()
    logging.getLogger('discord.commands').info("Command tree synced.")

bot.run(DISCORD_TOKEN)