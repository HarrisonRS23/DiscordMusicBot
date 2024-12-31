import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import yt_dlp
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_NUM = int(os.getenv("GUILD_ID"))

class Client(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.queue = []  # This will store the URLs of the songs in the queue
        self.is_playing = False  # Flag to check if the bot is playing a song

    async def on_ready(self): 
        print(f'Logged on as {self.user}')
        try: 
             guild = discord.Object(id=GUILD_NUM)
             synced = await self.tree.sync(guild=guild)
             print(f'Synced {len(synced)} commands to guild {guild.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    async def on_message(self, message):
        # if bot sends a message won't respond to itself
        if message.author == self.user:
            return
        # Respond to simple greetings
        lowercase = message.content.lower()
        if lowercase.startswith("hello"):
            await message.channel.send(f'Hi there {message.author}')
        if lowercase.startswith("bye"):
            await message.channel.send(f'See you later {message.author}!')
        if lowercase.startswith("who are you"):
            await message.channel.send(f'{message.author}, I am a Bot created by Harrison')

    async def on_reaction(self, reaction, user):
        await reaction.message.channel.send('You reacted')

    async def play_next(self, interaction: discord.Interaction):
        """Play the next song in the queue."""
        if self.queue:
            url = self.queue.pop(0)  # Get the first song in the queue
            await self.play_song(interaction, url)
        else:
            await interaction.followup.send("No more songs in the queue!")
            self.is_playing = False  # Mark that we are no longer playing

    async def play_song(self, interaction: discord.Interaction, url: str):
        """Play a song."""
        voice_client = interaction.guild.voice_client
        if not voice_client:
            await interaction.followup.send("Bot is not connected to a voice channel.")
            return

        # Get video info
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                title = info.get('title', 'Unknown Title')

            # Play the song
            source = discord.FFmpegPCMAudio(url2, options="-vn")
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.loop) if e is None else print(f"Error: {e}"))
            await interaction.followup.send(f"Now playing: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"Failed to play video: {e}")



intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Enable voice state-related events

client = Client(command_prefix="", intents=intents)

GUILD_ID = discord.Object(id=GUILD_NUM)

@client.event
async def on_voice_state_update(member, before, after):
    print(f"{member.name} changed their voice state.")

@client.tree.command(name="connect", description="Connect to your voice channel", guild=GUILD_ID)
async def connect(interaction: discord.Interaction):
    if interaction.user.voice:
        voice_channel = interaction.user.voice.channel
        if interaction.guild.voice_client is None:
            await voice_channel.connect()
            await interaction.response.send_message(f"Connected to {voice_channel.name}!")
        else:
            await interaction.guild.voice_client.move_to(voice_channel)
            await interaction.response.send_message(f"Moved to {voice_channel.name}!")
    else:
        await interaction.response.send_message("You need to join a voice channel first!", ephemeral=True)

@client.tree.command(name="play", description="Play a YouTube video", guild=GUILD_ID)
async def play(interaction: discord.Interaction, url: str):
    """Add a song to the queue and start playing if not already playing."""
    await interaction.response.defer()  # Defer the response to prevent timeout

    voice_client = interaction.guild.voice_client

    if not voice_client:
        if interaction.user.voice:
            voice_channel = interaction.user.voice.channel
            await voice_channel.connect()  # Connect to the user's voice channel
            await interaction.followup.send(f"Connected to {voice_channel.name}!")
        else:
            await interaction.followup.send("You need to join a voice channel first!", ephemeral=True)
            return

    # Add the song to the queue
    client.queue.append(url)

    # If the bot is not already playing, start playing the first song
    if not client.is_playing:
        client.is_playing = True
        await client.play_song(interaction, url)
    else:
        await interaction.followup.send(f"Added to queue: {url}")

@client.tree.command(name="skip", description="Skip the current song", guild=GUILD_ID)
async def skip(interaction: discord.Interaction):
    """Skip the current song."""
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("Skipped the current song.")
        await client.play_next(interaction)
    else:
        await interaction.response.send_message("No song is currently playing.")

@client.tree.command(name="queue", description="Show the current queue", guild=GUILD_ID)
async def queue(interaction: discord.Interaction):
    """Show the current queue."""
    if client.queue:
        queue_str = "\n".join(client.queue)
        await interaction.response.send_message(f"Current queue:\n{queue_str}")
    else:
        await interaction.response.send_message("The queue is empty.")

@client.tree.command(name="disconnect", description="Disconnect the bot from the voice channel",guild=GUILD_ID)
async def disconnecter(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:  # Check if the bot is in a voice channel
        await voice_client.disconnect()
        await interaction.response.send_message("Disconnected from the voice channel.")
    else:
        await interaction.response.send_message("I'm not connected to any voice channel.", ephemeral=True)

client.run(TOKEN)