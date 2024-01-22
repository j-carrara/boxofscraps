from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
import requests
from config import FFMPEG_OPTS, FFMPEG_PATH, CHANNEL, ADMIN_CHANNEL
import asyncio
import discord
import logging

def check(author):
    def inner_check(message):
        if message.author == author:
            try:
                number = int(message.content)
                if number > 0 and number <= 10:
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
                if ctx.channel.name == ADMIN_CHANNEL:
                    await interaction.response.defer(thinking=True, ephemeral=True)
                else:
                    await interaction.response.defer(thinking=True)
                result = 0
                try:
                    response = ydl.extract_info(f"ytsearch:{query}", download=False)['entries']
                except:
                    return (None, None, -1)
                info = response[0]
            else:
                result = 1
                results = YoutubeSearch(query, max_results=10).to_dict()
                await send_message(ctx, interaction, f"**Choose a video by number:**\n```"+'\n'.join([f'{i+1: >4}: {video["title"]} ({video["duration"]})' for i, video in enumerate(results)])+"```", False)
                try:
                    msg = await bot.wait_for('message', check=check(ctx.author), timeout=15)
                except:
                    await send_message(ctx, None, "Timed out.", False)
                    return (None, None, -1)
                selection = int(msg.content)
                try:
                    info = ydl.extract_info(f"https://youtube.com{results[selection-1]['url_suffix']}",download=False)
                except:
                    return (None, None, -1)
        else: 
            result = 0
            info = ydl.extract_info(query, download=False)
            
    for format in info['formats']:
        if 'acodec' in format and format['acodec'] != 'none':
            audio_source = format['url']
            break

    return (info, audio_source, result)

async def join(ctx, voice):
    if ctx.channel.name == ADMIN_CHANNEL:
        channel = ctx.guild.voice_channels[0]
    else:
        channel = ctx.author.voice.channel
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect() 

    return voice

async def send_message(ctx, interaction, message, thinking):
    if interaction != None:
        if thinking:
            await interaction.followup.send(message)
        else:
            if ctx.channel.name == ADMIN_CHANNEL:
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
                if ctx.channel.name == CHANNEL:
                    await ctx.channel.send(f'Now playing: "{now_playing[0]}".')
                channel.play(discord.FFmpegPCMAudio(source[0], **FFMPEG_OPTS, executable=FFMPEG_PATH), after=lambda e: asyncio.run_coroutine_threadsafe(queue_handler(bot, ctx, channel, song_queue, queue_lock, now_playing), bot.loop))
            else:
                now_playing[0] = None
                await ctx.guild.voice_client.disconnect()

async def song_handler(ctx, interaction, query, song_queue, now_playing, voice, queue_lock, bot, feeling_lucky):
    if query == None and song_queue.empty():
        return (-2, None)

    if query != None:
        video, source, result = await search(ctx, interaction, bot, query, feeling_lucky)
        if result == -1:
            return (result, None)
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

    return (result, title)

async def play_handler(ctx, query, bot, song_queue, now_playing, queue_lock, feeling_lucky=False):
    interaction = ctx.interaction

    if not (ctx.channel.name == CHANNEL or ctx.channel.name == ADMIN_CHANNEL):
        return

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)


    response, title = await song_handler(ctx, interaction, query, song_queue, now_playing, voice, queue_lock, bot, feeling_lucky)


    if ctx.channel.name == ADMIN_CHANNEL:
        logging.getLogger('discord.commands').info(f"{ctx.message.author}: {query}")
        if interaction == None: 
            await ctx.message.delete()
            return

    if not feeling_lucky:
        interaction = None
    
    if response == -1:
        await send_message(ctx, interaction, f"Error downloading specified video.", feeling_lucky)
        return

    if query == None and song_queue.empty():
        await send_message(ctx, interaction, f"Queue is empty, please input a song.", feeling_lucky)
    elif not (voice and voice.is_connected() and voice.is_playing()):
        await send_message(ctx, interaction, f'Now playing: "{now_playing[0]}".', feeling_lucky)
    else:
        await send_message(ctx, interaction, f'Queued: "{title}".', feeling_lucky)