import discord
from discord.ext import commands
import random
from faker import Faker  
import yt_dlp
import asyncio 
import aiohttp
import io

fake = Faker()

BOT_TOKEN = "YOUR BOT TOKEN" #replace with your bot token, you can get it from the discord developer portal

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states= True

bot =commands.Bot(command_prefix="!", intents=intents)

#ydl options

ydl_opts = {
    'format': 'bestaudio/best',
    "noplaylist": True,
    "quiet": True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

#ffmpeg options

ffmpeg_options = {
    'options': '-vn'
}

class MusicPlayer:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_playing = False

    async def play_next(self, ctx):
        if self.queue.empty():
            self.is_playing = False
            return

        self.is_playing = True
        url, title = await self.queue.get()

        source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
        ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), bot.loop))

        await ctx.send(f"🎶 Now playing: **{title}**")


music_players = {}


def search_youtube(query):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        entry = info["entries"][0]
        return entry["url"], entry["title"]


#bot events

@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = discord.utils.get(guild.text_channels, name="welcome🎲")

    if channel is None:
        try:
            channel = await guild.create_text_channel("welcome🎲")
        except discord.Forbidden:
            print("Bot does not have permission to create channels.")
            return
   
    if channel is not None:
        image_url = "Image URL here"  # Replace with your welcome image URL
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    return await channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())

                file = discord.File(data, 'welcome_image.png')

                embed = discord.Embed(
                    title=f"Welcome to the server, {member.name}!😊🎉",
                    description="We're glad to have you here!"
                )
                embed.set_image(url="attachment://welcome_image.png")
                await channel.send(file=file, embed=embed)

@bot.event
async def on_ready():
    #you can read this mesage only if you execute the code, how lucky👀
    print(f"Hello! {bot.user} is here to assist you")

#bot commands

@bot.command()
async def dicehelp(ctx):
   message=("I can teach you everything, the available commands are:"
    "\n roll <number 1-10> <d4,d6,d8,d10,d12,d20,d100> : to roll a dice of the specified type"
    "\n name <number 1-10> : to generate fake names"
    "\n play <song name or url> : to play a song in your voice channel (sadly not really fast yet)"
    "\n skip : to skip the current song"
    "\n stop : to stop the music and leave the voice channel"
   )
   await ctx.send(message)

@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first.")

    channel = ctx.author.voice.channel

    if not ctx.voice_client:
        await channel.connect()

    guild_id = ctx.guild.id

    if guild_id not in music_players:
        music_players[guild_id] = MusicPlayer()

    player = music_players[guild_id]

    url, title = search_youtube(query)

    await player.queue.put((url, title))
    await ctx.send(f"Added to queue: **{title}**")

    if not player.is_playing:
        await player.play_next(ctx)

@bot.command()
async def name(ctx, number: int):
    if number < 1 or number > 10:
        await ctx.send("Please provide a number between 1 and 10")
        return
    names = [fake.name() for _ in range(number)]
    await ctx.send("\n".join(names))
 
@bot.command()
async def skip(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

@bot.command()
async def roll(ctx, y: int, arg):
    if y < 1 or y > 10:
        await ctx.send("Please provide a number between 1 and 10 for the number of rolls")
        return
    
    for _ in range(y):
        if arg == "d4":
            x=random.randint(1,4)
        elif arg == "d6":
            x=random.randint(1,6)
            await ctx.send(x)
        elif arg == "d8":
            x=random.randint(1,8)
            await ctx.send(x)
        elif arg == "d10":
            x=random.randint(1,10)
            await ctx.send(x)
        elif arg == "d12":
            x=random.randint(1,12)
            await ctx.send(x)
        elif arg == "d20":
            x=random.randint(1,20)
            await ctx.send(x)
        elif arg == "d100":
            x=random.randint(1,100)
            await ctx.send(x)   
        else:
            await ctx.send("the command <$roll> accepts only dice's formats like d20 or d4")


bot.run(BOT_TOKEN)
