from youtube_dl import YoutubeDL
from youtube_search import YoutubeSearch
import requests
from config import FFMPEG_OPTS, FFMPEG_PATH
import asyncio
import discord

def check(author):
    def inner_check(message):
        if message.author == author:
            try:
                number = int(message.content)
                if number > 0 and number <= 5:
                    return True
            except:
                pass
        return False
    return inner_check

async def search(ctx, interaction, bot, query, feeling_lucky=False):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(query)
        except: 
            if feeling_lucky:
                result = 0
                response = ydl.extract_info(f"ytsearch:{query}", download=False)['entries']
                info = response[0]
            else:
                result = 1
                results = YoutubeSearch(query, max_results=10).to_dict()
                await send_message(ctx, interaction, f"**Choose a video by number:**\n```"+'\n'.join([f'{i+1: >4}: {video["title"]}' for i, video in enumerate(results)])+"```")
                try:
                    msg = await bot.wait_for('message', check=check(ctx.author), timeout=15)
                except:
                    await send_message(ctx, None, "Timed out.")
                    return (None, None, -1)
                selection = int(msg.content)
                info = ydl.extract_info(f"https://youtube.com{results[selection-1]['url_suffix']}",download=False)
        else: 
            result = 0
            info = ydl.extract_info(query, download=False)
    return (info, info['formats'][0]['url'], result)

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
        if ctx.channel.name == "moderator-only":
            await interaction.response.send_message(message, ephemeral=True)
        else:
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
                channel.play(discord.FFmpegPCMAudio(source[0], **FFMPEG_OPTS, executable=FFMPEG_PATH), after=lambda e: asyncio.run_coroutine_threadsafe(queue_handler(bot, ctx, channel, song_queue, queue_lock, now_playing), bot.loop))
            else:
                now_playing[0] = None
                await ctx.guild.voice_client.disconnect()

async def song_handler(ctx, interaction, query, song_queue, now_playing, voice, queue_lock, bot, feeling_lucky):
    if query == None and song_queue.empty():
        return True

    if query != None:
        video, source, result = await search(ctx, interaction, bot, query, feeling_lucky)
        if result == -1:
            return result
        title = video['title']
    else:
        title = None

    if not song_queue.empty() or (voice and voice.is_connected() and voice.is_playing()):            
        await song_queue.put((source, title))

    if not (voice and voice.is_connected() and voice.is_playing()):
        if song_queue.empty():
            now_playing[0] = title
        else:
            source = await song_queue.get()
            now_playing[0] = source[1]
            source = source[0]

        channel = await join(ctx, voice)
        channel.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS, executable=FFMPEG_PATH), after= lambda e: asyncio.run_coroutine_threadsafe(queue_handler(bot, ctx, channel, song_queue, queue_lock, now_playing), bot.loop))

    return result