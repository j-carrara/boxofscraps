import discord
from discord.ext import commands

import asyncio
import logging

from config import DISCORD_TOKEN
from command_tree import setup 
from util import send_message, song_handler

song_queue = asyncio.Queue()
queue_lock = asyncio.Lock()
now_playing = [None]

bot = commands.Bot(command_prefix="=", intents= discord.Intents.all())

@bot.event
async def on_ready():
    await setup(bot, play, stop, skip, queue, leave, clear)
    logging.getLogger('discord.commands').info("Command tree synced.")

@bot.command()
async def play(ctx, *, query=None, interaction=None):
    if not (ctx.channel.name == "bot-commands" or ctx.channel.name == "moderator-only"):
        return

    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    response = await song_handler(ctx, query, song_queue, now_playing, voice, queue_lock, bot)

    if ctx.channel.name == "moderator-only":
        logging.getLogger('discord.commands').info(f"{ctx.message.author}: {query}")
        if interaction == None: await ctx.message.delete()
        return

    if response["status"] == -1:
        await send_message(ctx, interaction, f"Queue is empty, please input a song.")
    elif response["status"] == 0:
        await send_message(ctx, interaction, f'Now playing: "{now_playing[0]}".')
    else:
        await send_message(ctx, interaction, f'Queued: "{response["title"]}".')

@bot.command()
async def stop(ctx, interaction=None):
    if ctx.channel.name == "bot-commands":
        if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
            await send_message(ctx, interaction, f'Stopping.')
            now_playing[0] = None
            await ctx.guild.voice_client.disconnect()
        else:
            await send_message(ctx, interaction, f"I'm not playing anything.")

@bot.command()
async def leave(ctx, interaction=None):
    stop(ctx, interaction)

@bot.command()
async def skip(ctx, interaction=None):
    if ctx.channel.name == "bot-commands":
        if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()
            await send_message(ctx, interaction, f'Skipping: "{now_playing[0]}".')
        else:
            await send_message(ctx, interaction, f"I'm not playing anything.")


@bot.command()
async def clear(ctx, interaction=None):
    if ctx.channel.name == "bot-commands":
        if song_queue.empty():
            if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
                ctx.guild.voice_client.stop()
                await send_message(ctx, interaction, "Queue cleared.")
            else:
                await send_message(ctx, interaction, "Queue already empty.")
        else:
            async with queue_lock:
                for _ in range(song_queue.qsize()):
                    await song_queue.get()
                if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
                    ctx.guild.voice_client.stop()
            
            await send_message(ctx, interaction, "Queue cleared.")
    
@bot.command()
async def queue(ctx, interaction=None):
    if ctx.channel.name == "bot-commands":
        if song_queue.empty():
            if now_playing[0] != None:
                await send_message(ctx, interaction, f"1: {now_playing[0]} [NOW PLAYING]")
            else:
                await send_message(ctx, interaction, "Queue is empty.")
        else:
            async with queue_lock:
                song_list = []
                for _ in range(song_queue.qsize()):
                    song_list.append(await song_queue.get())
                output = [song[1] for song in song_list]
                if now_playing[0] != None:
                    output.insert(0, f"{now_playing[0]} [NOW PLAYING]")
                output = '\n'.join([f"{i+1}: {v}" for i, v in enumerate(output)])
                await send_message(ctx, interaction, output)
                for song in song_list:
                    await song_queue.put(song)

bot.run(DISCORD_TOKEN)