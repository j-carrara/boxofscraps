from platform import system
from discord.opus import load_opus

# Your Discord application token
DISCORD_TOKEN = 'YOUR TOKEN HERE'

# FFMPEG library required, make sure to include path for whatever environment you run the bot on.
FFMPEG_LINUX_PATH = '/usr/local/bin/ffmpeg/ffmpeg-5.1.1-amd64-static/ffmpeg' 
FFMPEG_WINDOWS_PATH = r"C:\Users\Joe Carrara\Downloads\ffmpeg-2022-10-10-git-f3b5277057-full_build\bin\ffmpeg.exe"

# Prefix for chat commands
COMMAND_PREFIX = "="

# Channel that the bot will look in for general use
CHANNEL = "bot-commands" 

# OPTIONAL, /play in this channel will make the bot play in the first voice channel, even if the user is not connected. Commands here are deleted afterwords.
ADMIN_CHANNEL = "moderator-only" 

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

if system() == 'Windows':
    FFMPEG_PATH = FFMPEG_WINDOWS_PATH
else:
    load_opus('libopus.so.0')
    FFMPEG_PATH = FFMPEG_LINUX_PATH