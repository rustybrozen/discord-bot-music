import os
import discord
from discord.ext import commands
import yt_dlp
import asyncio
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

intents = discord.Intents.default()
intents.message_content = True

token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!', intents=intents)

STREAM_URLS = {
    "lofi1": "http://stream.laut.fm/lofi",  
    "funky": "https://www.youtube.com/watch?v=FUDn-1r15zQ"
}

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

async def get_youtube_audio_url(url):
    """Extract direct audio URL from a YouTube link using yt-dlp"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': False,
        'force_generic_extractor': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url'] if 'url' in info else None

@bot.command(name='play')
async def play(ctx, stream_key: str = "lofi1"):
    """Play music from stream URLs or YouTube"""
    if ctx.author.voice is None:
        await ctx.send("Bạn cần vào kênh thoại trước! 🚪")
        return

    stream_url = STREAM_URLS.get(stream_key.lower())
    
    if not stream_url:
        await ctx.send(f"Stream không hợp lệ. Các lựa chọn: {', '.join(STREAM_URLS.keys())}")
        return
    
    # If it's a YouTube link, extract the audio URL
    if "youtube.com" in stream_url or "youtu.be" in stream_url:
        stream_url = await get_youtube_audio_url(stream_url)
        if not stream_url:
            await ctx.send("Không thể lấy link audio từ YouTube.")
            return

    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if not voice_client:
        try:
            voice_client = await voice_channel.connect()
        except Exception as e:
            await ctx.send(f"Không thể kết nối: {str(e)}")
            return
    elif voice_client.channel != voice_channel:
        await voice_client.move_to(voice_channel)

    status_message = await ctx.send("⏳ Đang kết nối với stream...")

    try:
        if voice_client.is_playing():
            voice_client.stop()

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        audio_source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
        transformed_source = discord.PCMVolumeTransformer(audio_source, volume=0.5)

        voice_client.play(
            transformed_source,
            after=lambda e: print(f"Stream ended: {e}") if e else None
        )

        await status_message.edit(content=f"🎵 Đang phát: {stream_key}")

    except Exception as e:
        await status_message.edit(content=f"❌ Lỗi: {str(e)}")
        print(f"Error: {e}")

bot.run(token)

