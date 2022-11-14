import discord
from discord.ext import commands

import asyncio
import logging

from config import DISCORD_TOKEN, CHANNEL
from util import send_message, play_handler

song_queue = asyncio.Queue()
queue_lock = asyncio.Lock()
now_playing = [None]

bot = commands.Bot(command_prefix="=", intents= discord.Intents.all())

@bot.event
async def on_ready():
    await bot.tree.sync()
    logging.getLogger('discord.commands').info("Command tree synced.")

@bot.hybrid_command(name="play", with_app_command=True)
async def play(ctx, *, query):
    await play_handler(ctx, query, bot, song_queue, now_playing, queue_lock)

@bot.hybrid_command(name="feelinglucky", with_app_command=True)
async def feelinglucky(ctx, *, query):
    await play_handler(ctx, query, bot, song_queue, now_playing, queue_lock, feeling_lucky=True)

@bot.hybrid_command(name="fl", with_app_command=True)
async def fl(ctx, *, query):
    await play_handler(ctx, query, bot, song_queue, now_playing, queue_lock, feeling_lucky=True)

@bot.hybrid_command(name="stop", with_app_command=True)
async def stop(ctx):
    interaction = ctx.interaction
    if ctx.channel.name == CHANNEL:
        if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
            await send_message(ctx, interaction, f'Stopping.')
            now_playing[0] = None
            await ctx.guild.voice_client.disconnect()
        else:
            await send_message(ctx, interaction, f"I'm not playing anything.")

@bot.hybrid_command(name="leave", with_app_command=True)
async def leave(ctx):
    stop(ctx)

@bot.hybrid_command(name="skip", with_app_command=True)
async def skip(ctx):
    interaction = ctx.interaction
    if ctx.channel.name == CHANNEL:
        if ctx.guild.voice_client and ctx.guild.voice_client.is_connected() and ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.stop()
            await send_message(ctx, interaction, f'Skipping: "{now_playing[0]}".')
        else:
            await send_message(ctx, interaction, f"I'm not playing anything.")


@bot.hybrid_command(name="clear", with_app_command=True)
async def clear(ctx):
    interaction = ctx.interaction
    if ctx.channel.name == CHANNEL:
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
    
@bot.hybrid_command(name="queue", with_app_command=True)
async def queue(ctx):
    interaction = ctx.interaction
    if ctx.channel.name == CHANNEL:
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