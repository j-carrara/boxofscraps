from discord.ext import commands
import asyncio
from util import send_message, play_handler
from config import CHANNEL

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = asyncio.Queue()
        self.queue_lock = asyncio.Lock()
        self.now_playing = [None]


    @commands.hybrid_command(name="play", with_app_command=True, description="Search for/link a Youtube video to play in voice.")
    async def play(self, ctx, *, search_or_link):
        await play_handler(ctx, search_or_link, self.bot, self.song_queue, self.now_playing, self.queue_lock)

    @commands.hybrid_command(name="feelinglucky", with_app_command=True, description="Play the first result of a Youtube search in voice.")
    async def feelinglucky(self, ctx, *, search):
        await play_handler(ctx, search, self.bot, self.song_queue, self.now_playing, self.queue_lock, feeling_lucky=True)

    @commands.hybrid_command(name="fl", with_app_command=True, description="Play the first result of a Youtube search in voice.")
    async def fl(self, ctx, *, search):
        await play_handler(ctx, search, self.bot, self.song_queue, self.now_playing, self.queue_lock, feeling_lucky=True)

    @commands.hybrid_command(name="stop", with_app_command=True, description="Ends the current song and leaves.")
    async def stop(self, ctx):
        interaction = ctx.interaction
        if ctx.channel.name == CHANNEL:
            if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
                await send_message(ctx, interaction, f'Stopping.')
                self.now_playing[0] = None
                await ctx.guild.voice_client.disconnect()
            else:
                await send_message(ctx, interaction, f"I'm not playing anything.")

    @commands.hybrid_command(name="leave", with_app_command=True, description="Ends the current song and leaves.")
    async def leave(self, ctx):
        self.stop(ctx)

    @commands.hybrid_command(name="skip", with_app_command=True, description="Skips the current song.")
    async def skip(self, ctx):
        interaction = ctx.interaction
        if ctx.channel.name == CHANNEL:
            if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
                ctx.guild.voice_client.stop()
                await send_message(ctx, interaction, f'Skipping: "{self.now_playing[0]}".')
            else:
                await send_message(ctx, interaction, f"I'm not playing anything.")


    @commands.hybrid_command(name="clear", with_app_command=True, description="Empties the song queue.")
    async def clear(self, ctx):
        interaction = ctx.interaction
        if ctx.channel.name == CHANNEL:
            if self.song_queue.empty():
                if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
                    ctx.guild.voice_client.stop()
                    await send_message(ctx, interaction, "Queue cleared.")
                else:
                    await send_message(ctx, interaction, "Queue already empty.")
            else:
                async with self.queue_lock:
                    for _ in range(self.song_queue.qsize()):
                        await self.song_queue.get()
                    if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
                        ctx.guild.voice_client.stop()
                
                await send_message(ctx, interaction, "Queue cleared.")
        
    @commands.hybrid_command(name="queue", with_app_command=True, description="Displays the current queue.")
    async def queue(self, ctx):
        interaction = ctx.interaction
        if ctx.channel.name == CHANNEL:
            if self.song_queue.empty():
                if self.now_playing[0] != None:
                    await send_message(ctx, interaction, f"1: {self.now_playing[0]} [NOW PLAYING]")
                else:
                    await send_message(ctx, interaction, "Queue is empty.")
            else:
                async with self.queue_lock:
                    song_list = []
                    for _ in range(self.song_queue.qsize()):
                        song_list.append(await self.song_queue.get())
                    output = [song[1] for song in song_list]
                    if self.now_playing[0] != None:
                        output.insert(0, f"{self.now_playing[0]} [NOW PLAYING]")
                    output = '\n'.join([f"{i+1}: {v}" for i, v in enumerate(output)])
                    await send_message(ctx, interaction, output)
                    for song in song_list:
                        await self.song_queue.put(song)