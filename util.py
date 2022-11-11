from youtube_dl import YoutubeDL
import requests
from config import FFMPEG_OPTS, FFMPEG_PATH
import asyncio
from discord import FFmpegPCMAudio

def search(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(query)
        except: info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        else: info = ydl.extract_info(query, download=False)
    return (info, info['formats'][0]['url'])

async def join(ctx, voice):
    if ctx.channel.name == "moderator-only":
        channel = ctx.guild.voice_channels[0]
    else:
        channel = ctx.author.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect() 

    return voice

async def send_message(ctx, interaction, message):
    if interaction != None:
        await interaction.response.send_message(message)
    else:
        await ctx.channel.send(message)

async def queue_handler(bot, ctx, channel, song_queue, queue_lock, now_playing):
    async with queue_lock:
        if ctx.guild.voice_client and ctx.guild.voice_client.is_connected():
            if not song_queue.empty():
                source = await song_queue.get()
                now_playing[0] = source[1]
                if ctx.channel.name == "bot-commands":
                    await ctx.channel.send(f'Now playing: "{now_playing[0]}".')
                channel.play(FFmpegPCMAudio(source[0], **FFMPEG_OPTS, executable=FFMPEG_PATH), after=lambda e: asyncio.run_coroutine_threadsafe(queue_handler(bot, ctx, channel, song_queue, queue_lock, now_playing), bot.loop))
            else:
                now_playing[0] = None
                await ctx.guild.voice_client.disconnect()