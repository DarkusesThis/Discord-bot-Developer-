import discord
from discord import app_commands
import google.generativeai as genai
from flask import Flask
import threading
import os

# --- Configurations ---
# We will use Environment Variables in Render to keep these safe!
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') 

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}! The /rscript command is ready.')

@client.tree.command(name="rscript", description="Searches for a human-like, handwritten Roblox script")
async def rscript(interaction: discord.Interaction, query: str):
    await interaction.response.defer() 
    
    prompt = f"""
    You are an expert Roblox Lua developer active on the DevForum. 
    A user is asking for the following script: "{query}".
    Provide the most authentic, handwritten, and optimized Roblox Lua script for this request. 
    Do not write it like a generic AI. Use proper spacing, logical variable names, and common developer conventions. 
    Provide ONLY the code block and a 1-2 sentence explanation of where to place it.
    """
    
    try:
        response = model.generate_content(prompt)
        reply_text = response.text
        if len(reply_text) > 2000:
            reply_text = reply_text[:1990] + "\n...[Cut off due to Discord limits]"
        await interaction.followup.send(reply_text)
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {e}")

# --- The Render Web Server Hack ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is online and running!"

def run_server():
    # Render assigns a dynamic port, this catches it
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Start the web server in the background
threading.Thread(target=run_server).start()

# Start the Discord bot
client.run(DISCORD_TOKEN)
  
