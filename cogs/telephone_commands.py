import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
import databas as database
SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class telephone_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @app_commands.command(
            name='message',
            description='envoie un message'
    )
    @app_commands.guild_only()
    async def message(self,interaction:discord.Interaction,destinataire:discord.User,image:discord.Attachment=None,*,message:str):
        try:
            await interaction.response.defer(ephemeral=True)
            chan:discord.channel= interaction.guild.get_channel(int(os.getenv("ADMIN_CHANNEL")))
            embed_admin=discord.Embed(title="message envoyé:",description=f'<@!{interaction.user.id}> a envoyé un message à <@!{destinataire.id}>',color=0x00ebeb)
            embed_admin.add_field(name="contenu du message: ",value=message+"\n\u200b")
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            file_thumbnail=discord.File('images/appel.gif',filename="appel.gif")

            embed_admin.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            embed_admin.set_thumbnail(url='attachment://appel.gif')
            if(image!=None):
                file=await image.to_file(filename=image.filename)
                embed_admin.set_image(url=image.url)
            await chan.send(files=[file_logo,file_thumbnail],embed=embed_admin)
            embed_send=discord.Embed(title="contenu du message: ",description=message,color=0x00ebeb)
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            file_thumbnail=discord.File('images/appel.gif',filename="appel.gif")
            if(image!=None):
                file=await image.to_file(filename=image.filename)
                embed_send.set_image(url=image.url)
            embed_send.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            embed_send.set_thumbnail(url='attachment://appel.gif')
            await destinataire.send(files=[file_logo,file_thumbnail],embed=embed_send,content=f"Vous avez reçu un message de <@!{interaction.user.id}>:")
            embed_confirm=discord.Embed(title="\u200b",description=f"📱 Votre message a bien été envoyé a <@!{destinataire.id}>",color=0x00ebeb)
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            file_thumbnail=discord.File('images/appel.gif',filename="appel.gif")
            embed_confirm.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            embed_confirm.set_thumbnail(url='attachment://appel.gif')
            if(image!=None):
                file=await image.to_file(filename=image.filename)
                embed_confirm.set_image(url=image.url)
            await interaction.followup.send(files=[file_logo,file_thumbnail],embed=embed_confirm,ephemeral=True)
        except Exception as error:
            print(error)
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            embed_confirm=discord.Embed(title="\u200b",description=f"🚫 Une erreur est survenu votre message n'a pas pû être envoyé",color=0x00ebeb)
            embed_confirm.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            embed_confirm.set_thumbnail(url='attachment://logo_realis_rp_anime.gif')
            await interaction.followup.send(file=file_logo,embed=embed_confirm,ephemeral=True)
    
    @app_commands.command(
            name='911',
            description="appel un service d'urgence"
    )
    @app_commands.guild_only()
    @app_commands.choices(service=[
        app_commands.Choice(name="LSPD", value="LSPD"),
        app_commands.Choice(name="EMS", value="EMS"),
        app_commands.Choice(name="Tout", value="tout"),
        ])
    async def service_911(self,interaction:discord.Interaction,service:app_commands.Choice[str],*,lieu:str,nature:str):
        await interaction.response.defer()
        if(service.value=="LSPD" or service.value=="tout"):
            channel=interaction.guild.get_channel(int(os.getenv("LSPD_CHANNEL")))
            embed=discord.Embed(
                title=" 🚔  Appel LSPD  🚔 ",
                description=f"Nom : <@!{interaction.user.id}>\nLieu : {lieu}\nNature de l'appel : {nature}",
                color=0x00ebeb
            )
            file1=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            file2=discord.File('images/LSPD.png',filename="LSPD.png")

            embed.set_thumbnail(url='attachment://LSPD.png')
            embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')

            await channel.send(content=f"<@&{os.getenv('LSPD_ID')}>",files=[file1,file2], embed=embed)
            
        if(service.value=="EMS" or service.value=="tout"):
            channel=interaction.guild.get_channel(int(os.getenv("EMS_CHANNEL")))
            embed=discord.Embed(
                title=" 🚑  Appel EMS  🚑 ",
                description=f"Nom : <@!{interaction.user.id}>\nLieu : {lieu}\nNature de l'appel : {nature}",
                color=0x00ebeb
            )
            file1=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            file2=discord.File('images/EMS.png',filename="EMS.png")
            embed.set_thumbnail(url='attachment://EMS.png')
            embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')

            await channel.send(content=f"<@&{os.getenv('EMS_ID')}>",files=[file1,file2], embed=embed)            
        if(service.value=="tout"):
            embed=discord.Embed(
                title="🚑  Votre appel à bien été transmit aux services sélectionnés, des équipes sont en route 🚔",
                color=0x00ebeb
            )
        else:
            embed=discord.Embed(
                title="🚑  Votre appel à bien été transmit au service sélectionné, une équipe est en route 🚔",
                color=0x00ebeb
            )
        file1=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        file2=discord.File('images/dispatch.png',filename="dispatch.png")
        embed.set_thumbnail(url='attachment://dispatch.png')
        embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')

        await interaction.followup.send(content=f"<@!{interaction.user.id}>",embed=embed,files=[file1,file2])
        
        if(service.value=="EMS" or service.value=="LSP" or service.value=="tout"):
            try:
                voice_channel=interaction.user.voice.channel
                if voice_channel:
                    vc=await voice_channel.connect()
                    vc.play(discord.FFmpegPCMAudio("./audio/audio.mp3"))
                    while vc.is_playing():
                        await asyncio.sleep(.1)
                    await vc.disconnect() 
            except Exception as error:
                print(error)


    @app_commands.command(
            name='ano',
            description="envoie d'un message anonyme"
    )
    @app_commands.guild_only()
    async def ano(self,interaction:discord.Interaction,image:discord.Attachment=None,*,message:str):
        await interaction.response.defer(ephemeral=True)
        chan:discord.channel= interaction.guild.get_channel(int(os.getenv("ADMIN_CHANNEL")))
        embed_admin=discord.Embed(title="message anonyme envoyé:",description=f'<@!{interaction.user.id}> a envoyé un message anonyme',color=0x00ebeb)
        embed_admin.add_field(name="contenu du message: ",value=message+"\n\u200b")
        file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        embed_admin.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
        embed_admin.set_thumbnail(url='attachment://logo_realis_rp_anime.gif')
        embed_ano=discord.Embed(title="message anonyme: ",description=message+"\n\u200b",color=0x00ebeb)
        if(image!=None):
            file=await image.to_file(filename=image.filename)
            embed_admin.set_image(url=image.url)
        await chan.send(file=file_logo,embed=embed_admin)

        if(image!=None):
            file=await image.to_file(filename=image.filename)
            embed_ano.set_image(url=image.url)
        file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        embed_ano.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
        await interaction.channel.send(file=file_logo,embed=embed_ano)
        await interaction.followup.send(content="Votre message anonyme a bien été envoyé",ephemeral=True)

async def setup(bot):
    await bot.add_cog(telephone_commands_cog(bot))
    