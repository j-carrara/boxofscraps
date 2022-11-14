from platform import system
from discord.opus import load_opus

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
DISCORD_TOKEN = '***REMOVED***'
FFMPEG_LINUX_PATH = '/usr/local/bin/ffmpeg/ffmpeg-5.1.1-amd64-static/ffmpeg'
FFMPEG_WINDOWS_PATH = r"C:\Users\Joe Carrara\Downloads\ffmpeg-2022-10-10-git-f3b5277057-full_build\bin\ffmpeg.exe"
CHANNEL = "bot-commands"
ADMIN_CHANNEL = "moderator-only"

if system() == 'Windows':
    FFMPEG_PATH = FFMPEG_WINDOWS_PATH
else:
    load_opus('libopus.so.0')
    FFMPEG_PATH = FFMPEG_LINUX_PATH