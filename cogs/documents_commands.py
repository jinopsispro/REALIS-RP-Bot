import io
import os
import discord
from discord.ext import commands
import requests
from discord import app_commands
from discord.ui import Button,View
import databas as database
from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont

class cgView(discord.ui.View):
    def __init__(self,base_interaction,joueur,CI,PC,PA,CG,*,timeout=None):
        super().__init__(timeout=timeout or 180)
        self.base_interaction=base_interaction
        self.CI=CI
        self.PC=PC
        self.PA=PA
        self.CG=list(CG)
        self.joueur=joueur
        self.add_select()        
    @discord.ui.button(
        label="retour",
        row=1
    )
    async def retour(self,interaction:discord.Interaction,button:discord.ui.Button):
        embed=discord.Embed(title="🌇Realis RP🌇",description=f"Votre portefeuille comporte vos papiers d'identités",color=0x00ebeb)
        view=Buttons(self.base_interaction,self.joueur,self.CI,self.PC,self.PA,self.CG)
        await interaction.response.edit_message(attachments=[],content=f"<@!{self.joueur.id}>",embed=embed,view=view)
    async def create_image_cg(self,avatar,cg):
        img = Image.open("images\\carte_grise.png")
        response = requests.get(avatar)
        img2= Image.open(io.BytesIO(response.content)).resize((300,300))
        fontForImg = ImageFont.truetype("arialbd.ttf", 42, encoding="unic")
        draw = ImageDraw.Draw(img)
        img.paste(img2,(249,195))
        W=800
        msg=self.CI["nom"]
        _, _, w, _=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text((30+(W-w)/2, 600),msg,(0,0,0),font=fontForImg)
        W=800
        msg=self.CI["prenom"]
        _, _, w,_=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text((30+(W-w)/2, 750),msg,(0,0,0),font=fontForImg)

        msg=cg["modele"]
        draw.text((1050, 240),msg,(0,0,0),font=fontForImg)
        msg=cg["immatriculation"]
        draw.text((1050, 440),msg,(0,0,0),font=fontForImg)
        msg=cg["date_circulation"].strftime("%d/%m/%Y")
        draw.text((1050, 640),msg,(0,0,0),font=fontForImg)
        return img

    def get_liste_options(self,liste):
        liste_np=[]
        for i in liste:
            liste_np.append(discord.SelectOption(label=f"{i['modele']}",description=f"{i['immatriculation']}",value=str(i["immatriculation"])))
        return liste_np
    
    def add_select(self):
        liste=self.get_liste_options(self.CG)
        
        select=discord.ui.Select(options=liste,row=0)
        async def selectChange(interaction:discord.Interaction):
            msg=interaction.message.id
            await interaction.response.defer()
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            selected=database.get_carte_grise_immat(select.values[0])
            button=discord.ui.Button(label="retour")
            async def retour(interaction:discord.Interaction):
                desc=f"**Vous avez trouver ces cartes grises de** \n<@!{self.joueur.id}>\n"
                for cg in self.CG:
                    desc+=f"\u25CF **{cg['modele']}** - {cg['immatriculation']} ｜｜ **{cg['date_circulation'].strftime('%d/%m/%Y')}**\n"
                embed=discord.Embed(title="🌇Realis RP🌇",description=desc,color=0x00ebeb)
                view=cgView(self.base_interaction,self.joueur,self.CI,self.PC,self.PA,self.CG)
                await interaction.response.edit_message(attachments=[],content=f"<@!{self.joueur.id}>",embed=embed,view=view)
            
            button.callback=retour
            
            view=discord.ui.View()
            view.add_item(button)

            image=await self.create_image_cg(self.joueur.display_avatar,selected)
            image_file=None
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                image_file=discord.File(fp=image_binary, filename='image.png')

            await interaction.followup.edit_message(message_id=msg,attachments=[image_file],view=view,embed=None)
        
        select.callback=selectChange
        self.add_item(select)

class Buttons(discord.ui.View):
    def __init__(self,base_interaction,joueur,CI,PC,PA,CG,*,timeout=None):
        super().__init__(timeout=timeout or 180)
        self.base_interaction=base_interaction
        self.CI=CI
        self.PC=PC
        self.PA=PA
        self.CG=list(CG)
        self.joueur=joueur
        self.add_buttons()  

    async def create_image_carte_id(self,avatar):
        img = Image.open("images\\carte_identite.png")
        response = requests.get(avatar)

        img2= img2= Image.open(io.BytesIO(response.content)).resize((218,215))
        fontForImg = ImageFont.truetype("arialbd.ttf", 28, encoding="unic")
        
        draw = ImageDraw.Draw(img)

        img.paste(img2,(78,126))

        msg=self.CI["nom"]
        draw.text((330, 118),msg,(0,0,0),font=fontForImg)
        msg=self.CI["prenom"]
        draw.text((330, 160),msg,(0,0,0),font=fontForImg)
        msg=self.CI["date_de_naissance"].strftime("%d/%m/%Y")
        draw.text((330, 211),msg,(0,0,0),font=fontForImg)
        msg=self.CI["nationalite"]
        draw.text((330, 256),msg,(0,0,0),font=fontForImg)
        msg=self.CI["genre"]
        draw.text((330, 297),msg,(0,0,0),font=fontForImg) 
        return img

    async def create_image_pc(self,avatar):
        img = Image.open("images\\permis_modele2.png")
        response = requests.get(avatar)
        img2= Image.open(io.BytesIO(response.content)).resize((300,300))

        fontForImg = ImageFont.truetype("arialbd.ttf", 32, encoding="unic")
        
        draw = ImageDraw.Draw(img)

        img.paste(img2,(168,175))

        W=668
        msg=self.PC["nom"]
        _, _, w, _=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text(((W-w)/2, 570),msg,(0,0,0),font=fontForImg)
        msg=self.PC["prenom"]
        _, _, w,_=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text(((W-w)/2, 720),msg,(0,0,0),font=fontForImg)
        msg=self.PC["date_de_naissance"].strftime("%d/%m/%Y")
        _, _, w,_=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text(((W-w)/2, 870),msg,(0,0,0),font=fontForImg)
        if(self.PC["permis_voiture"]):
            draw.text((750, 335),f"Obtenu le {self.PC['date_permis_voiture'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((750, 335),f"Non Obtenu",(0,0,0),font=fontForImg)
        if(self.PC["permis_camion"]):
            draw.text((750, 605),f"Obtenu le {self.PC['date_permis_camion'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((750, 605),f"Non obtenu",(0,0,0),font=fontForImg)

        if(self.PC["permis_helicoptere"]):
            draw.text((750, 875),f"Obtenu le {self.PC['date_permis_helicoptere'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((750, 875),f"Non obtenu",(0,0,0),font=fontForImg)
        if(self.PC["permis_moto"]):
            draw.text((1350, 335),f"Obtenu le {self.PC['date_permis_moto'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((1350, 335),f"Non Obtenu",(0,0,0),font=fontForImg)
        if(self.PC["permis_bateau"]):
            draw.text((1350, 605),f"Obtenu le {self.PC['date_permis_bateau'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((1350, 605),f"Non obtenu",(0,0,0),font=fontForImg)

        if(self.PC["permis_avion"]):
            draw.text((1350, 875),f"Obtenu le {self.PC['date_permis_avion'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((1350, 875),f"Non obtenu",(0,0,0),font=fontForImg)
        return img
        
    async def create_image_pa(self,avatar,nom,prenom,pa_lourde,pa_legere,pa_blanche):
        img = Image.open("images\\permis_armes_modele.png")
        response = requests.get(avatar)
        img2= Image.open(io.BytesIO(response.content)).resize((300,300))

        fontForImg = ImageFont.truetype("arialbd.ttf", 32, encoding="unic")
        
        draw = ImageDraw.Draw(img)

        img.paste(img2,(249,195))

        W=800
        msg=nom
        _, _, w, _=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text((30+(W-w)/2, 600),msg,(0,0,0),font=fontForImg)
        W=800
        msg=prenom
        _, _, w,_=draw.textbbox((60,600),msg,font=fontForImg)
        draw.text((30+(W-w)/2, 750),msg,(0,0,0),font=fontForImg)

        if(pa_legere):
            draw.text((1180, 245),f"Obtenu le {self.PA['date_permis_legere'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((1180, 245),f"Non Obtenu",(0,0,0),font=fontForImg)
        if(pa_lourde):
            draw.text((1180, 445),f"Obtenu le {self.PA['date_permis_lourde'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((1180, 445),f"Non obtenu",(0,0,0),font=fontForImg)

        if(pa_blanche):
            draw.text((1180, 645),f"Obtenu le {self.PA['date_permis_blanche'].strftime('%d/%m/%Y')}",(0,0,0),font=fontForImg)
        else:
            draw.text((1180, 645),f"Non obtenu",(0,0,0),font=fontForImg)
        return img

    def add_buttons(self):
        ci_button=discord.ui.Button(label="🪪 Carte Identité",
            style=discord.ButtonStyle.success if(self.CI!=None) else discord.ButtonStyle.danger,
            disabled=self.CI==None
        )
        async def carte_identite(interaction: discord.Interaction):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            msg=interaction.message.id
            await interaction.response.defer()
            button=discord.ui.Button(label="retour")
            async def retour(interaction:discord.Interaction):
                    staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
                    if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                        return
                    embed=discord.Embed(title="🌇Realis RP🌇",description=f"Votre portefeuille comporte vos papiers d'identités",color=0x00ebeb)
                    view=Buttons(self.base_interaction,self.joueur,self.CI,self.PC,self.PA,self.CG)
                    await interaction.response.edit_message(attachments=[],content=f"<@!{self.joueur.id}>",embed=embed,view=view)
            button.callback=retour
            view=discord.ui.View()
            view.add_item(button)

            image=await self.create_image_carte_id(self.joueur.display_avatar)
            image_file=None
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                image_file=discord.File(fp=image_binary, filename='image.png')

            await interaction.followup.edit_message(message_id=msg,attachments=[image_file],view=view,embed=None)

        ci_button.callback=carte_identite
        self.add_item(ci_button)
        pc_button=discord.ui.Button(label="🚙 Permis de conduire",
            style=discord.ButtonStyle.success if(self.PC!=None) else discord.ButtonStyle.danger,
            disabled=self.PC==None
        )
        async def permis_conduire(interaction: discord.Interaction):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            msg=interaction.message.id
            await interaction.response.defer()
            button=discord.ui.Button(label="retour")
            async def retour(interaction:discord.Interaction):
                    staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
                    if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                        return
                    embed=discord.Embed(title="🌇Realis RP🌇",description=f"Votre portefeuille comporte vos papiers d'identités",color=0x00ebeb)
                    view=Buttons(self.base_interaction,self.joueur,self.CI,self.PC,self.PA,self.CG)
                    await interaction.response.edit_message(attachments=[],content=f"<@!{self.joueur.id}>",embed=embed,view=view)
            button.callback=retour
            view=discord.ui.View()
            view.add_item(button)
            image=await self.create_image_pc(self.joueur.display_avatar)
            image_file=None
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                image_file=discord.File(fp=image_binary, filename='image.png')

            await interaction.followup.edit_message(message_id=msg,attachments=[image_file],view=view,embed=None)

        pc_button.callback=permis_conduire
        self.add_item(pc_button)
        pa_button=discord.ui.Button(label="Permis Port Arme",
            style=discord.ButtonStyle.success if(self.PA!=None) else discord.ButtonStyle.danger,
            disabled=self.PA==None
        )
        async def permis_port_arme(interaction: discord.Interaction):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return 
            msg=interaction.message.id
            await interaction.response.defer()
          
            button=discord.ui.Button(label="retour")
            async def retour(interaction:discord.Interaction):
                    staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
                    if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                        return
                    embed=discord.Embed(title="🌇Realis RP🌇",description=f"Votre portefeuille comporte vos papiers d'identités",color=0x00ebeb)
                    view=Buttons(self.base_interaction,self.joueur,self.CI,self.PC,self.PA,self.CG)
                    await interaction.response.edit_message(attachments=[],content=f"<@!{self.joueur.id}>",embed=embed,view=view)
            button.callback=retour
            view=discord.ui.View()
            view.add_item(button)
            image=await self.create_image_pa(self.joueur.display_avatar,self.PA["nom"],self.PA["prenom"],self.PA["permis_arme_lourde"],self.PA["permis_arme_legere"],self.PA["permis_arme_blanche"])
            image_file=None
            with io.BytesIO() as image_binary:
                image.save(image_binary, 'PNG')
                image_binary.seek(0)
                image_file=discord.File(fp=image_binary, filename='image.png')

            await interaction.followup.edit_message(message_id=msg,attachments=[image_file],view=view,embed=None)
        pa_button.callback=permis_port_arme
        self.add_item(pa_button)
        cg_button=discord.ui.Button(label="🚙 Carte Grise",
            style= discord.ButtonStyle.success if(len(self.CG)>0) else discord.ButtonStyle.danger,
            disabled=len(self.CG)<=0
        )
        async def carte_grise(interaction:discord.Interaction):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            view=cgView(self.base_interaction,self.joueur,self.CI,self.PC,self.PA,self.CG)
            desc=f"**Vous avez trouver ces cartes grises de \n<@!{self.joueur.id}>\n"
            for cg in self.CG:
                desc+=f"\u25CF **{cg['modele']}** - {cg['immatriculation']} ｜｜ **{cg['date_circulation'].strftime('%d/%m/%Y')}**\n"
            embed=discord.Embed(title="🌇Realis RP🌇",description=desc,color=0x00ebeb)
            await interaction.response.edit_message(view=view,embed=embed)
        cg_button.callback=carte_grise
        self.add_item(cg_button) 

    
SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class documents_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
    def get_liquide(self,user:discord.User):
        return database.get_argent_liquide(str(user.id))["cash"]
    def getCI(self,user:discord.User):
        try:
            return database.get_identite(discord_ID=str(user.id))
        except:
            return None

    def getPC(self,user:discord.User):
        try:
            pc= database.get_permis_de_conduire(discord_ID=str(user.id))
            if(pc["permis_voiture"] or pc["permis_moto"] or pc["permis_camion"] or pc["permis_bateau"] or pc["permis_avion"] or pc["permis_helicoptere"]):
                return pc
            else: return None
        except Exception as e:
            print(e)
            return None
    def getPA(self,user:discord.User):
        try:
            pa= database.get_permis_port_arme(discord_ID=str(user.id))
            if(pa["permis_arme_legere"] or pa["permis_arme_lourde"] or pa["permis_arme_blanche"]):
                return pa
            else: return None
        except Exception as e:
            print(e)
            return None

    def getCG(self,user:discord.User):
        return database.get_carte_grise_joueur(discord_ID=str(user.id))
    
    @app_commands.command(
        name='portefeuille',
        description="affiche le portefeuille d'un joueur"
    )    
    @app_commands.guild_only()
    async def portefeuille(self,interaction:discord.Interaction,joueur:discord.User=None):
        await interaction.response.defer()
        if(joueur==None): joueur=interaction.user
        embed=discord.Embed(title="🌇Realis RP🌇",description=f"Votre portefeuille comporte vos papiers d'identités",color=0x00ebeb)
        ci=self.getCI(joueur)
        if(ci==None):
            view=Buttons(interaction,interaction.user,None,None,None,[])
        else:
            view=Buttons(interaction,interaction.user,self.getCI(joueur),self.getPC(joueur),self.getPA(joueur),self.getCG(joueur))

        await interaction.followup.send(content=f"<@!{interaction.user.id}>",embed=embed,view=view)

    @app_commands.command(
        name='carte-identité-créer',
        description="crée une carte d'identité"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("LSPD_ID")),int(os.getenv("NOTAIRE_ID")))
    async def carte_identite_creer(self,interaction:discord.Interaction,prenom:str,nom:str,genre:str,jour:int,mois:int,annee:int,*,lieu_de_naissance:str,nationalite:str,joueur:discord.User):
        try:
            database.cree_identite(str(joueur.id),prenom,nom,genre,jour,mois,annee,lieu_de_naissance,nationalite)
            database.cree_inventaire(str(joueur.id))
            await interaction.response.send_message(f"🪪  La carte d'identité de <@!{joueur.id}> a bien été créer !")
        except Exception as e:
            await interaction.response.send_message(f"Une erreur est survenu pendant la création de la carte d'identité de {joueur.id}")
            print(e)

    @app_commands.command(
        name='carte-grise-créer',
        description="crée la carte grise d'un joueur"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("LSPD_ID")))
    async def carte_grise_creer(self,interaction:discord.Interaction,immatriculation:str,modele:str,joueur:discord.User):
        await interaction.response.defer()
        try:
            if(not database.cree_carte_grise(str(joueur.id),immatriculation,modele)):
                await interaction.followup.send(f"<@!{joueur.id}> ne possède pas de carte d'identité")
                return
            await interaction.followup.send(f"La carte grise de <@!{joueur.id}> a bien été créer !")
        except Exception as e:
            print(e)
            await interaction.followup.send(f"Une erreur est survenu pendant la création de la carte grise de <@!{joueur.id}> ce joueur possède-t-il une carte d'identité ?")

    @app_commands.command(
        name='carte-grise-supprimer',
        description="supprime une carte grise d'un joueur"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("LSPD_ID")))
    async def carte_grise_supprimer(self,interaction:discord.Interaction,immatriculation:str):
        await interaction.response.defer()
        try:
            cg=database.get_carte_grise_immat(immatriculation)
            identite=database.get_identite_from_id(str(cg['id_identite']))
            joueur=interaction.guild.get_member(int(identite['id_discord']))
            if(cg!=None):
                embed=discord.Embed(title=f"{immatriculation} : {joueur.display_name} :",description=f"🚙  Vous avez bien retiré la carte grise immatriculée {immatriculation} !",color=0x00ebeb)
                database.supprime_carte_grise(immatriculation)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(content=f"Il n'existe pas de carte grise pour l'immatriculation {immatriculation}")
        except Exception as e:
            print(e)
            await interaction.followup.send(content="une erreur est survenue")

    @app_commands.command(
        name='permis-de-conduire-créer',
        description='crée un permis de conduire'
    )
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("MONITEUR_ID")))
    @app_commands.choices(type_vehicule=[
        app_commands.Choice(name="Voiture", value="voiture"),
        app_commands.Choice(name="Moto", value="moto"),
        app_commands.Choice(name="Camion", value="camion"),
        app_commands.Choice(name="Bateau", value="bateau"),
        app_commands.Choice(name="Avion", value="avion"),
        app_commands.Choice(name="Helicoptere", value="helicoptere"),
        ])
    async def permis_de_conduire_creer(self,interaction:discord.Interaction,type_vehicule:app_commands.Choice[str],joueur:discord.User):
        try:
            if(not database.cree_permis_de_conduire(str(joueur.id),type_vehicule.value)):
                await interaction.response.send_message(f"<@!{joueur.id}> ne possède pas de carte d'identité")
                return
            inv=database.get_inventaire(str(joueur.id))
            try:
                pc=inv["permis_conduire"]
                if(not pc):
                    database.add_permis_conduire_inventaire(str(joueur.id))
            except StopIteration:
                print("pas d'inventaire trouvé")
                
            await interaction.response.send_message(f"🅿️ <@!{joueur.id}> possède désormais le permis {type_vehicule.value} !")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"Une erreur est survenu pendant la création du permis de <@!{joueur.id}>")
        
    @app_commands.command(
        name="permis-de-port-darme-créer",
        description="crer un permis de port d'arme"
    )    
    @app_commands.choices(type_arme=[
        app_commands.Choice(name="Arme lourde",value="lourde"),
        app_commands.Choice(name="Arme légère",value="legere"),
        app_commands.Choice(name="Arme blanche",value="blanche"),
    ])
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("LSPD_ID")),int(os.getenv("ARMURIER_ID")))
    async def permis_de_port_darme_creer(self,interaction:discord.Interaction,joueur:discord.User,type_arme:app_commands.Choice[str]):
        try:
            if(not database.cree_permis_port_arme(str(joueur.id),type_arme.value)):
                await interaction.response.send_message(f"<@!{joueur.id}> ne possède pas de carte d'identité")
                return
            await interaction.response.send_message(f"🔫 <@!{joueur.id}> possède désormais le permis port d'arme {type_arme.value} ! ")
            inv=database.get_inventaire(str(joueur.id))
            if(not inv['permis_port_arme'] ):
                database.add_permis_inventaire(str(joueur.id))
        except:
            await interaction.response.send_message("erreur pendant la création du permis")


    @app_commands.command(
        name='permis-de-conduire-retiré',
        description='retire un permis de conduire'    
        )    
    @app_commands.choices(type_vehicule=[
        app_commands.Choice(name="Voiture", value="voiture"),
        app_commands.Choice(name="Moto", value="moto"),
        app_commands.Choice(name="Camion", value="camion"),
        app_commands.Choice(name="Bateau", value="bateau"),
        app_commands.Choice(name="Avion", value="avion"),
        app_commands.Choice(name="Helicoptere", value="helicoptere"),
    ])
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("LSPD_ID")),int(os.getenv("MONITEUR_ID")))
    async def permis_de_conduire_retirer(self,interaction:discord.Interaction,joueur:discord.User,type_vehicule:app_commands.Choice[str]):
        try:
            database.retire_permis_conduire(str(joueur.id),type_vehicule.value)
            id=database.get_permis_de_conduire(str(joueur.id))
            if(not id["permis_voiture"] and not id["permis_moto"] and not id["permis_camion"] and not id['permis_bateau'] and not id["permis_avion"] and not id['permis_helicoptere']):
                database.remove_permis_conduire_inventaire(str(joueur.id))
            await interaction.response.send_message(f"🪪 Vous avez bien retiré le permis {type_vehicule.value} à <@!{joueur.id}> !")

        except Exception as e:
            print(e)
            await interaction.response.send_message("erreur supprimer permis")

    @app_commands.command(
        name="permis-de-port-darme-retiré",
        description="retire un permis de port d'arme"
    )    
    @app_commands.choices(type_arme=[
        app_commands.Choice(name="Arme lourde",value="lourde"),
        app_commands.Choice(name="Arme légère",value="legere"),
        app_commands.Choice(name="Arme blanche",value="blanche"),
    ])
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("LSPD_ID")),int(os.getenv("ARMURIER_ID")))
    async def permis_de_port_darme_retirer(self,interaction:discord.Interaction,joueur:discord.User,type_arme:app_commands.Choice[str]):
        try:
            database.retire_permis_port_arme(str(joueur.id),type_arme.value)
            id=database.get_permis_port_arme(str(joueur.id))
            if(not id["permis_arme_lourde"] and not id["permis_arme_legere"] and not id["permis_arme_blanche"] ):
                database.remove_permis_inventaire(str(joueur.id))
            await interaction.response.send_message(f"🔫 <@!{joueur.id}> ne possède plus le permis port d'arme {type_arme.value} ! ")

        except Exception as e:
            print(e)
            await interaction.response.send_message("erreur pendant la création du permis")

    
async def setup(bot):
    await bot.add_cog(documents_commands_cog(bot))

    