import datetime
import os
import discord
from discord.ext import commands
from discord import app_commands
import databas as database

SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class police_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    def get_noms_prenoms(self,liste):
        liste_np=[]
        for i in liste:
            liste_np.append(discord.SelectOption(label=f"{i['nom']} {i['prenom']}",description=f"<@!{i['id_discord']}>",value=i))
        return liste_np
    @app_commands.command(
        name='recherche-de-personne',
        description='recherche une personne'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','LSPD')
    async def recherche_persone(self,interaction:discord.Interaction,nom:str,prenom:str):
        ids=database.find_identite(nom,prenom)
        liste_ids=list(ids)
        if(len(liste_ids)==0):
            await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embed=discord.Embed(title="recherche d'information civile",description=f"{nom} {prenom} n'est pas recensée",color=0x00ebeb))
            return
        if(len(liste_ids)>1):
            liste_noms=self.get_noms_prenoms(liste_ids)
            select=discord.ui.Select(options=liste_noms)
            async def select_callback(interaction:discord.Interaction,select:discord.ui.Select):
                staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
                if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                    return
                embed=discord.Embed(title="recherche d'information civile",color=0x00ebeb)
                selected=select.values[0]
                embed.add_field(name="Nom",value=selected["nom"],inline=False)
                embed.add_field(name="Prénom",value=selected["prenom"],inline=False)
                embed.add_field(name="Sexe",value=selected["genre"],inline=False)
                embed.add_field(name="Date de naissance",value=selected["date_de_naissance"].strftime("%d/%m/%Y"),inline=False)
                embed.add_field(name="Lieu de naissance",value=selected["lieu_de_naissance"],inline=False)
                embed.add_field(name="Nationalité",value=selected["nationalite"],inline=False)
                await interaction.response.edit_message(embed=embed,view=None)
            select.callback=select_callback
            view=discord.ui.View()
            view.add_item(select)
            await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embed=discord.Embed(title="recherche d'information civile",description="plusieurs personnes ont été trouvé possédant ce nom et prénom"),view=view,color=0x00ebeb)
        else:
            embed=discord.Embed(title="recherche d'information civile",color=0x00ebeb)
            selected=liste_ids[0]
            embed.add_field(name="Nom",value=selected["nom"],inline=False)
            embed.add_field(name="Prénom",value=selected["prenom"],inline=False)
            embed.add_field(name="Sexe",value=selected["genre"],inline=False)
            embed.add_field(name="Date de naissance",value=selected["date_de_naissance"].strftime("%d/%m/%Y"),inline=False)
            embed.add_field(name="Lieu de naissance",value=selected["lieu_de_naissance"],inline=False)
            embed.add_field(name="Nationalité",value=selected["nationalite"],inline=False)
            await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embed=embed)

    @app_commands.command(
        name='recherche-de-plaque',
        description='recherche la plaque'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','LSPD')
    async def recherche_plaque(self,interaction:discord.Interaction,immatriculation:str):
        plaque=database.get_carte_grise_immat(str(immatriculation))
        id=database.get_identite_from_id(plaque["id_identite"])
        embed_vehicule=discord.Embed(title="Recherche d'information de Véhicule",color=0x00ebeb)
        embed_vehicule.add_field(name="Modele",value=f"{plaque['modele']}",inline=False)
        embed_vehicule.add_field(name="Plaque",value=f"{plaque['immatriculation']}",inline=False)
        embed_vehicule.add_field(name="date de circulation",value=f"{plaque['date_circulation']}",inline=False)
        embed_identite=discord.Embed(color=0x00ebeb)
        embed_identite.add_field(name="Nom",value=id['nom'],inline=False)
        embed_identite.add_field(name="Prenom",value=id['prenom'],inline=False)
        embed_identite.add_field(name="Sexe",value=id['genre'],inline=False)

        embed_identite.add_field(name="Date de naissance",value=id['date_de_naissance'].strftime("%d/%m/%Y"),inline=False)
        await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embeds=[embed_vehicule,embed_identite])
    
    @app_commands.command(
        name='service-prendre-lspd',
        description='prise de service LSPD'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','LSPD')
    async def service_prendre_lspd(self,interaction:discord.Interaction):
        embed=discord.Embed(title="RealisRP",color=0x00ff00)
        embed.add_field(name="Entreprise/Département",value="LSPD",inline=False)
        embed.add_field(name="Qui?",value=f"<@!{interaction.user.id}>",inline=False)
        embed.add_field(name="Statut",value="Prise de service",inline=False)
        timestamp=datetime.datetime.now().timestamp()
        embed.set_footer(text=f"<T:{timestamp}>")
        file=discord.File('images/LSPD.png',filename="LSPD.png")
        embed.set_thumbnail(url="attachment://LSPD.png")
        await interaction.response.send_message(file=file,content=f"<@!{interaction.user.id}>",embed=embed)

    @app_commands.command(
        name='service-finir-lspd',
        description='fin de service LSPD'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','LSPD')
    async def service_finir_lspd(self,interaction:discord.Interaction):
        embed=discord.Embed(title="RealisRP",color=0xff0000)
        embed.add_field(name="Entreprise/Département",value="LSPD",inline=False)
        embed.add_field(name="Qui?",value=f"<@!{interaction.user.id}>",inline=False)
        embed.add_field(name="Statut",value="Fin de service",inline=False)
        timestamp=datetime.datetime.now().timestamp()
        embed.set_footer(text=f"<T:{timestamp}>")
        file=discord.File('images/LSPD.png',filename="LSPD.png")
        embed.set_thumbnail(url="attachment://LSPD.png")
        await interaction.response.send_message(file=file,content=f"<@!{interaction.user.id}>",embed=embed)

    @app_commands.command(
        name='service-prendre-ems',
        description='prise de service EMS'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','EMS')
    async def service_prendre_ems(self,interaction:discord.Interaction):
        embed=discord.Embed(title="RealisRP",color=0x00ff00)
        embed.add_field(name="Entreprise/Département",value="EMS",inline=False)
        embed.add_field(name="Qui?",value=f"<@!{interaction.user.id}>",inline=False)
        embed.add_field(name="Statut",value="Prise de service",inline=False)
        timestamp=datetime.datetime.now().timestamp()
        embed.set_footer(text=f"<T:{timestamp}>")
        file=discord.File('images/EMS.png',filename="EMS.png")
        embed.set_thumbnail(url="attachment://EMS.png")
        await interaction.response.send_message(file=file,content=f"<@!{interaction.user.id}>",embed=embed)
    @app_commands.command(
        name='service-finir-ems',
        description='fin de service EMS'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','EMS')
    async def service_finir_ems(self,interaction:discord.Interaction):
        embed=discord.Embed(title="RealisRP",color=0xff0000)
        embed.add_field(name="Entreprise/Département",value="EMS",inline=False)
        embed.add_field(name="Qui?",value=f"<@!{interaction.user.id}>",inline=False)
        embed.add_field(name="Statut",value="Fin de service",inline=False)
        file=discord.File('images/EMS.png',filename="EMS.png")
        embed.set_thumbnail(url="attachment://EMS.png")
        timestamp=datetime.datetime.now().timestamp()
        embed.set_footer(text=f"<T:{timestamp}>")
        await interaction.response.send_message(file=file,content=f"<@!{interaction.user.id}>",embed=embed)
    def get_liste_vol(self,liste_objets):
        l_objets=liste_objets["SAC_NOMS"]
        l_qtt=liste_objets["SAC_QUANTITE"]
        l=[]
        for i in range(len(l_objets)):
            lab=l_objets[i]+" : "+str(l_qtt[i])+("g" if(" traitée" in l_objets[i]) else "x")
            l.append(discord.SelectOption(label=lab,value=l_objets[i]))
        l.append(discord.SelectOption(label=f"Argent : {liste_objets['cash']}",value="Argent"))
        return l
    
    def get_i(self,liste,nom):
        return liste.index(nom)
    @app_commands.command(
        name='confisque',
        description="confisque des items ou de l'argent à quelqu'un"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','LSPD')
    async def confisquer(self,interaction:discord.Interaction,cible:discord.User):
        inv=database.get_inventaire(str(interaction.user.id))
        if(inv==None):
            await interaction.response.send_message(content="Vous ne possédez pas d'inventaire")
            return
        embed=discord.Embed(title="Confisquation",description="Choisissez ce que vous voulez confisquer à cette personne")
        objets=database.get_inventaire(str(cible.id))
        if(objets==None):
            await interaction.response.send_message(content="la cible ne possède pas d'inventaire")
            return
        select=discord.ui.Select(options=self.get_liste_vol(objets))
        async def select_cb(interaction:discord.Interaction):
            selected=select.values[0]
            msg=interaction.message
            modal=discord.ui.Modal(title="quantité")
            if(selected=="Argent"):
                text=discord.ui.TextInput(label=f"cette personne possède {objets['cash']}$")
            else:
                i=self.get_i(objets["SAC_NOMS"],selected)
                text=discord.ui.TextInput(label=f"cette personne possède {objets['SAC_QUANTITE'][i]}{'g' if(' traitée' in objets['SAC_NOMS'][i]) else 'x'} {objets['SAC_NOMS'][i]}")
            async def on_submit(interaction:discord.Interaction):   
                proba=50/100
                if(selected=="Argent"):
                    if(database.retire_argent_liquide(cible.id,float(text.value))):
                        database.ajoute_argent_liquide(interaction.user.id,float(text.value))
                        await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] Vous avez confisqué {text.value.removesuffix('.0')}$ à <@!{cible.id}>. 🎉💸")
                    else:
                        await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] <@!{cible.id}> ne possède pas {text.value.removesuffix('.0')}$. 🎉💸")
                else:
                    qtt=database.retirer_objet_inventaire(cible.id,selected,int(text.value))
                    database.ajouter_objet_inventaire(interaction.user.id,selected,int(qtt))
                    await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] Vous avez confisqué {qtt}{'g' if(' traitée' in objets['SAC_NOMS'][i]) else ''} {selected} à <@!{cible.id}>. 🎉💸")
            modal.add_item(text)
            modal.on_submit=on_submit
            await interaction.response.send_modal(modal)
        select.callback=select_cb
        view=discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embed=embed,view=view)

async def setup(bot):
    await bot.add_cog(police_commands_cog(bot))