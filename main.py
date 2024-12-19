import os
import discord
from discord.ext import commands
from discord import app_commands
from pymongo import MongoClient
TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('SERVER_ID')
class MonBot(commands.Bot):
    async def setup_hook(self):
        for extension in ['bank_commands','bot_commands','boutique_commands','delit_commands','documents_commands','police_commands','session_commands','telephone_commands']:
            await self.load_extension(f'cogs.{extension}')

intents = discord.Intents.default()
intents.message_content = True
intents.members=True
bot = MonBot(command_prefix='/',intents=intents)
bot.help_command=None
bot.run(token=TOKEN)
