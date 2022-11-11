from discord.ext import commands
from discord import app_commands, Interaction

class BoxOfCommands(commands.Cog):
    def __init__(self, bot: commands.Bot, play, stop, skip, queue, leave, clear) -> None:
        self.bot = bot
        self.play = play
        self.stop = stop
        self.skip = skip
        self.queue = queue
        self.leave = leave
        self.clear = clear

    @app_commands.command(name="play", description="Search or link something to play in voice.")
    async def app_play(self, interaction: Interaction, search_or_link: str) -> None:
        await self.play(await self.bot.get_context(interaction), query=search_or_link, interaction=interaction)
    
    @app_commands.command(name="stop", description="Removes the bot from the channel and ends the current song.")
    async def app_stop(self, interaction: Interaction) -> None:
        await self.stop(await self.bot.get_context(interaction), interaction=interaction)

    @app_commands.command(name="skip", description="Skips the current song.")
    async def app_skip(self, interaction: Interaction) -> None:
        await self.skip(await self.bot.get_context(interaction), interaction=interaction)

    @app_commands.command(name="queue", description="Displays the current queue.")
    async def app_queue(self, interaction: Interaction) -> None:
        await self.queue(await self.bot.get_context(interaction), interaction=interaction)

    @app_commands.command(name="leave", description="Forces the bot to leave a voice channel.")
    async def app_leave(self, interaction: Interaction) -> None:
        await self.leave(await self.bot.get_context(interaction), interaction=interaction)

    @app_commands.command(name="clear", description="Empties the whole damn song queue.")
    async def app_clear(self, interaction: Interaction) -> None:
        await self.clear(await self.bot.get_context(interaction), interaction=interaction)

async def setup(bot: commands.Bot, play, stop, skip, queue, leave, clear) -> None:
  await bot.add_cog(BoxOfCommands(bot, play, stop, skip, queue, leave, clear))
  await bot.tree.sync()