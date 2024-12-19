import os
import discord
from discord.ext import commands
from discord import app_commands
import databas as database

SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class session_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @app_commands.command(
        name='session-annoncer',
        description='annoncer une session'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def session_annoncer(self,interaction:discord.Interaction,heure:str,lanceur:discord.User=None):
        embed=discord.Embed(
            title="✈️  -  **Nouvelle session** ",
            color=0x00ebeb
        )
        embed.add_field(value=f"⏰ **Heure**: {heure}",name="\0",inline=False)
        embed.add_field(value=f"👤 **Lanceur**: <@!{interaction.user.id if lanceur==None else lanceur.id}>",name="\0",inline=False)
        embed.add_field(value="",name="\0") 
        embed.add_field(value="✅  Présent  -  ❌  Absent  -  ⏰  En retard\n\u200b",name="Rappel des réactions:",inline=False)
        file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        file_image=discord.File('images/annoucementSession.gif',filename="annoucementSession.gif")
        embed.set_thumbnail(url='attachment://annoucementSession.gif')
        embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
        await interaction.response.send_message(content=f"<@&{os.getenv('CITOYEN_ID')}>",files=[file_logo,file_image],embed=embed)
        response=await interaction.original_response()
        await response.add_reaction('✅')
        await response.add_reaction('❌')
        await response.add_reaction('⏰')

    @app_commands.command(
        name='session_début',
        description="début d'une session RP"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def session_debut(self,interaction:discord.Interaction,lanceur:discord.User=None):
        embed=discord.Embed(
            title="✈️  Début de la session ! ",
            description=f"La session va débuter ! \nIdentifiez <@!{interaction.user.id if lanceur==None else lanceur.id}> pour qu'il vous invite ! ",
            color=0x00ebeb
        )
        file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        file_image=discord.File('images/startSession.gif',filename="startSession.gif")
        embed.set_thumbnail(url='attachment://startSession.gif')
        embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
        await interaction.response.send_message(content=f"<@&{os.getenv('CITOYEN_ID')}>",files=[file_logo,file_image],embed=embed)

    @app_commands.command(
        name='action-rp',
        description='effectuer une action rp avec image'
    )    
    @app_commands.guild_only()
    async def action_rp(self,interaction:discord.Interaction,image:discord.Attachment=None,*,action:str):
        identite=database.get_identite(str(interaction.user.id))
        embed=discord.Embed(title=f"{identite['nom']} {identite['prenom']} ({interaction.user.display_name}) est en train d'effectuer l'action suivante:",description=f"{action} \n\u200b",color=0x00ebeb)
        file=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        embed.set_footer(text=interaction.user.display_name,icon_url=interaction.user.display_avatar.url)
        if(image!=None):
            file=await image.to_file(filename=image.filename)
            embed.set_image(url=image.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='session-fin',
        description='fin de la session'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def session_fin(self,interaction:discord.Interaction):
        embed=discord.Embed(
            title="🛬  Fin de la session ! ",
            description=f"La session est terminée !\n On vous laisse finir vos scènes, bonne nuit ! ",
            color=0x00ebeb
        )
        file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        file_image=discord.File('images/endSession.gif',filename="endSession.gif")
        embed.set_thumbnail(url='attachment://endSession.gif')
        embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
        await interaction.response.send_message(content=f"<@&{os.getenv('CITOYEN_ID')}>",files=[file_image,file_logo],embed=embed)

    @app_commands.command(
        name='mort-rp',
        description="mort-rp d'un joueur"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def mort_rp(self,interaction:discord.Interaction,joueur:discord.User):
        try:
            database.mort_rp(str(joueur.id))
            await interaction.response.send_message(f"⚰️ La mort rp de <@!{joueur.id}> a bien été confirmée ! ")
        except:
            await interaction.response.send_message("une erreur est survenue attention certaine donnée peuvent quand même avoir été supprimées")

async def setup(bot):
    await bot.add_cog(session_commands_cog(bot))