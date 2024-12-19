import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import databas as database
from typing import Callable, Optional

SERVER_ID = os.getenv('SERVER_ID')

class Pagination(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, get_page: Callable):
        self.interaction = interaction
        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.interaction.user:
            return True
        else:
            emb = discord.Embed(
                description=f"Only the author of the command can perform this action.",
                color=16711680
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    async def navegate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.interaction.response.send_message(embed=emb)
        elif self.total_pages > 1:
            self.update_buttons()
            await self.interaction.response.send_message(embed=emb, view=self)

    async def edit_page(self, interaction: discord.Interaction):
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await interaction.response.edit_message(embed=emb, view=self)

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, interaction: discord.Interaction, button: discord.Button):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.Button):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, interaction: discord.Interaction, button: discord.Button):
        if self.index <= self.total_pages//2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        message = await self.interaction.original_response()
        await message.edit(view=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1

@app_commands.guilds(discord.Object(id = SERVER_ID))
class MyBot(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
    @app_commands.command(name='help',description="affiche cet embed")
    async def help(self,interaction:discord.Interaction):
        appcommands=self.bot.tree.get_commands()
        async def get_page(page:int):
            n=Pagination.compute_total_pages(len(appcommands),10)
            emb=discord.Embed(title=f"Page {page}/{n}",description="",color=0x00ebeb)
            offset=(page-1)*10
            for command in appcommands[offset:offset+10]:
                emb.description+=f"**{command.name}:**\n\u200b \u200b \u200b {command.description}\n"
            return emb,n
        await Pagination(interaction,get_page).navegate()
    
    @commands.command('sync')
    async def sync(self,ctx:commands.Context):
        if(ctx.author.id==238945878331752448):
            fmt=await self.bot.tree.sync(guild=None)
            print(f'Syncd {len(fmt)} commands to global at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
            return
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Logged on as {self.bot.user}!')

async def setup(bot):
    await bot.add_cog(MyBot(bot))