import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = os.getenv("DISCORD_BOT_TOKEN")


class Client(commands.Bot):

    # called whenever bot has connected
    async def on_ready(self): 
        print(f'logged on as {self.user}')


        try: 
             guild = discord.Object(id=GUILD_ID)
             synced = await self.tree.sync(guild=guild)
             print (f'Synced {len(synced)} commands to guild {guild.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')

    
    async def on_message(self,message):
        # if bot sends a message wont respond to itself
        if message.author == self.user:
            return
        # if someone sends a message starting with hello bot will respond 
        lowercase = message.content.lower()
        if lowercase.startswith("hello"):
            await message.channel.send(f'Hi there {message.author}' )
        if lowercase.startswith("bye"):
            await message.channel.send(f'See you later {message.author}!')
        if lowercase.startswith("who are you"):
            await message.channel.send(f'{message.author}, I am a Bot created by Harrison')
    
    async def on_reaction(self,reaction,user):
        await reaction.message.channel.send('You reacted')
        
    

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Enable voice state-related events

# command prefix used to be how to interact with bots and is now replaced with slash commands
client = Client(command_prefix="", intents=intents) 

@client.event
async def on_voice_state_update(member, before, after):
    print(f"{member.name} changed their voice state.")



# id of developement server so that slash command only pushed to dev server while making changes
GUILD_ID = discord.Object(id=GUILD_ID)

# name is name of slash command and must be lowercase
@client.tree.command(name= "hello", description="Say hello!", guild=GUILD_ID)
async def say_hello(interaction: discord.Interaction):
    # respond to slash command with send messsage
    await interaction.response.send_message("Hello there")

@client.tree.command(name= "printer", description="I will print whatever you give me", guild=GUILD_ID)
async def printer(interaction: discord.Interaction, printer: str):
    # respond to slash command with send messsage
    await interaction.response.send_message(printer)

@client.tree.command(name= "play", description="I will play a youtube video" , guild=GUILD_ID)
async def printer(interaction: discord.Interaction, youtube: str):
    # respond to slash command with send messsage
    #await interaction.response.send_message(youtube)
    embed = discord.Embed(title="Youtube title", url = 'https://www.youtube.com', description= "youtube description", color=discord.Color.red())
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/2560px-YouTube_full-color_icon_%282017%29.svg.png")
    embed.add_field(name="video", value= "video info")
    embed.set_author(name=interaction.user.name)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name= "connect", description="I will connect to your channel" , guild=GUILD_ID)
async def connecter(interaction: discord.Interaction):
    if interaction.user.voice:  # Check if the user is in a voice channel
        voice_channel = interaction.user.voice.channel
        # Connect to the user's current voice channel
        if interaction.guild.voice_client is None:
            await voice_channel.connect()
            await interaction.response.send_message(f"Connected to {voice_channel.name}!")
        else:
            await interaction.guild.voice_client.move_to(voice_channel)
            await interaction.response.send_message(f"Moved to {voice_channel.name}!")
        
    else:
        await interaction.response.send_message("You need to join a voice channel first!", ephemeral=True)

@client.tree.command(name="disconnect", description="Disconnect the bot from the voice channel")
async def disconnecter(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:  # Check if the bot is in a voice channel
        await voice_client.disconnect()
        await interaction.response.send_message("Disconnected from the voice channel.")
    else:
        await interaction.response.send_message("I'm not connected to any voice channel.", ephemeral=True)

client.run(TOKEN)