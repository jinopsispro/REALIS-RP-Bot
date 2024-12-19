import asyncio
import datetime
import time
import os
import discord
from discord.ext import commands
from discord import app_commands
import databas as database
import random
class customView(discord.ui.View):
    def __init__(self,base_interaction,drg,bool,timeout=None):
        super().__init__(timeout=timeout or 900)
        self.base_interaction=base_interaction
        self.drg=drg
        self.add_button_vente(bool)

    @discord.ui.button(label="récolte",style=discord.ButtonStyle.blurple)
    async def recolte(self,interaction:discord.Interaction,button:discord.ui.Button):
        if(database.get_id(str(self.base_interaction.user.id))==None):
            await interaction.response.edit_message(embed=None,view=None,content="Vous devez posséder une identité pour récolter de la drogue",color=0xff0000)
        
        msg=interaction.message
        ctime=datetime.datetime.now()+datetime.timedelta(seconds=self.drg["temps_recolte"]*60)
        timestamp=int(ctime.timestamp())
        embed=discord.Embed(title=f"Récolte de {self.drg['nom']} en cours ...",description=f"<@!{self.base_interaction.user.id}>. Vous êtes en train de récolter: {self.drg['nom']}\nFin de la récolte: <t:{timestamp}:R>",color=0xff0000)
        await interaction.response.edit_message(embed=embed,view=None)
        await asyncio.sleep(self.drg['temps_recolte']*60)
        embed=discord.Embed(title=f"Récolte de {self.drg['nom']} terminée",description=f"<@!{self.base_interaction.user.id}>. Vous avez récolté **{self.drg['quantite']}g** de {self.drg['nom']}\n\nVous pouvez dès à présent traiter votre drogue",color=0x00ff00)
        database.ajouter_objet_inventaire(str(self.base_interaction.user.id),self.drg["nom"]+" non traitée",self.drg["quantite"])
        await msg.edit(embed=embed,view=None)

    @discord.ui.button(label="Traitement",style=discord.ButtonStyle.green)
    async def traitement(self,interaction:discord.Interaction,button:discord.ui.Button):
        if(database.get_id(str(self.base_interaction.user.id))==None):
            await interaction.response.edit_message(embed=None,view=None,content="Vous devez posséder une identité pour traiter de la drogue",color=0xff0000)
        max_qtt=database.get_qtt_item(str(self.base_interaction.user.id),str(self.drg['nom']+" non traitée"))
        if(max_qtt<=0):
            await interaction.response.send_message(content="Veuillez récolter cette drogue avant de la traiter",ephemeral=True,color=0xff0000)
            return
        qtt=database.retirer_objet_inventaire(str(self.base_interaction.user.id),self.drg["nom"]+" non traitée",self.drg["quantite"])
        msg=interaction.message
        if(qtt>0):
            ctime=datetime.datetime.now()+datetime.timedelta(seconds=self.drg["temps_traitement"]*60)
            timestamp=int(ctime.timestamp())
            embed=discord.Embed(title=f"Traitement de {self.drg['nom']} en cours ...",description=f"<@!{self.base_interaction.user.id}>. Vous êtes en train de Traiter: {qtt}g de {self.drg['nom']}\nFin du traitement: <t:{timestamp}:R>",color=0xff0000)
            await interaction.response.edit_message(embed=embed,view=None)
            await asyncio.sleep(self.drg['temps_traitement']*60)
            embed=discord.Embed(title=f"Récolte de {self.drg['nom']} terminée",description=f"<@!{self.base_interaction.user.id}>. Vous avez récolté **{self.drg['quantite']}g** de {self.drg['nom']}\n\nVous pouvez dès à présent vendre votre drogue",color=0x00ff00)
            database.ajouter_objet_inventaire(str(self.base_interaction.user.id),self.drg["nom"]+" traitée",self.drg["quantite"])
            await msg.edit(embed=embed,view=None)
    def add_button_vente(self,bool):
        button=discord.ui.Button(label="Vente",style=discord.ButtonStyle.danger,disabled= bool)
        async def bcall(interaction:discord.Interaction):
            if(database.get_id(str(self.base_interaction.user.id))==None):
                await interaction.response.edit_message(embed=None,view=None,content="Vous devez posséder une identité pour traiter de la drogue",color=0xff0000)
                return
            msg=interaction.message
            modal=discord.ui.Modal(title=f"Quantité de {self.drg['nom']} traitée à vendre:")
            max_qtt=database.get_qtt_item(str(self.base_interaction.user.id),str(self.drg['nom']+" traitée"))
            if(max_qtt<=0):
                await interaction.response.send_message(content="Veuillez traiter la drogue avant de la vendre.",ephemeral=True)
                return
            txt=discord.ui.TextInput(label=f"Vous en possédez {max_qtt}g")
            lieu=discord.ui.TextInput(label="Lieu de vente",placeholder="1-10")
            modal.add_item(txt)
            modal.add_item(lieu)
            async def on_submit(interaction: discord.Interaction):
                chan=interaction.guild.get_channel(int(os.getenv("LSPD_CHANNEL")))
                qtt_choix=int(txt.value)
                qtt=database.retirer_objet_inventaire(str(self.base_interaction.user.id),self.drg["nom"]+" traitée",qtt_choix)
                await interaction.response.edit_message(content=msg.content)
                if(qtt>0):
                    ctime=datetime.datetime.now()+datetime.timedelta(seconds=self.drg["temps_vente"]*60)
                    timestamp=int(ctime.timestamp())
                    embed=discord.Embed(title=f"Vente de {self.drg['nom']} en cours ...",description=f"<@!{self.base_interaction.user.id}>. Vous êtes en train de Vendre: {qtt}g de {self.drg['nom']}\nFin de vente: <t:{timestamp}:R>",color=0xff0000)
                    await chan.send(content=f"Une vente de drogue est en cours à {lieu.value}")
                    await msg.edit(embed=embed,view=None)
                    await asyncio.sleep(self.drg["temps_vente"]*60)
                    qttQ2=int(qtt*random.uniform(0.15,0.3)*100)/100
                    qttQ3=int(qtt*random.uniform(0.15,0.25)*100)/100
                    qttQ4=int(qtt*random.uniform(0.15,0.2)*100)/100
                    qttQ1=int((qtt-qttQ2-qttQ3-qttQ4)*100)/100
                    gain=qttQ1*self.drg["prix_qualite1"]+qttQ2*self.drg["prix_qualite2"]+qttQ3*self.drg["prix_qualite3"]+qttQ4*self.drg["prix_qualite4"]
                    embed=discord.Embed(title=f"Vente de {self.drg['nom']} terminée",description=f"<@!{self.base_interaction.user.id}>. Vous avez Vendu **{qtt}g** de {self.drg['nom']}\n\nVous avez gagné {str(gain).removesuffix('.0')}$\n{qttQ1}g mauvaise qualité:{qttQ1*self.drg['prix_qualite1']}$\n{qttQ2}g qualité moyenne:{qttQ2*self.drg['prix_qualite2']}$\n{qttQ3}g bonne qualité:{qttQ3*self.drg['prix_qualite3']}$\n{qttQ4}g très bonne qualité:{qttQ4*self.drg['prix_qualite4']}$",color=0x00ff00)
                    database.ajoute_argent_liquide(str(self.base_interaction.user.id),gain)
                    await msg.edit(embed=embed,view=None)
            modal.on_submit=on_submit
            await interaction.response.send_modal(modal)
        button.callback=bcall
        self.add_item(button)

SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class delit_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @app_commands.command(
        name="drogue-creer",
        description="cree une drogue"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def drogue_creer(self,interaction:discord.Interaction,nom:str,quantité:int,temps_recolte:float,temps_traitement:float,image:str=None):
        try:
            inp=database.cree_drog(nom=nom,quantite=quantité,tps_recolte=temps_recolte,tps_traitement=temps_traitement,image=image)
            await interaction.response.send_message(f"{nom} créée avec succès ! 🎉")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"une erreur est survenue pendant la création de {nom}")


    @app_commands.command(
        name="drogue-modifier",
        description="modifie une drogue"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def drogue_modifier(self,interaction:discord.Interaction,nom:str,quantité:int=None,temps_recolte:float=None,temps_traitement:float=None,image:str=None):
        try:
            result=database.modifier_drog(nom=nom,quantite=quantité,tps_recolte=temps_recolte,tps_traitement=temps_traitement,image=image)
            if(result.matched_count>0):
                await interaction.response.send_message(f"Drogue {nom} modifiée avec succès ! ✏️")
            else:
                await interaction.response.send_message(f"Drogue {nom} non trouvée")

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"une erreur est survenue pendant la modification de {nom}")

    def get_liste_drgs(self,drgs):
        l=[]
        for doc in drgs:
            l.append(discord.SelectOption(label=doc["nom"],value=doc["nom"]))
        return l

    @app_commands.command(
        name="drogue-afficher",
        description="afficher une drogue"
    )    
    @app_commands.guild_only()
    async def drogue_afficher(self,interaction:discord.Interaction):
        drgs=list(database.get_drogs())
        view=discord.ui.View()
        select=discord.ui.Select(options=self.get_liste_drgs(drgs))
        async def select_cb(interaction:discord.Interaction):
            nom=select.values[0]
            dr=database.get_drog_infos(nom)
            err=""
            b=False
            try:
                pq1=dr["prix_qualite1"]
                pq4=dr["prix_qualite1"]
                tps=dr["temps_vente"]
            except:
                pq1="?"
                pq4="?"
                tps="?"
                err="\nLa vente de cette drogue n'a pas encore été parametrée"
                b=True
            embed=discord.Embed(title=f"Drogue: {nom}",color=0x00ebeb)
            embed.add_field(name="Récolte potentielle:",value=f"{dr['quantite']}",inline=False)
            embed.add_field(name="Gains potentiels:",value=f"{str(pq1).removesuffix('.0')}$-{str(pq4).removesuffix('.0')}$",inline=False)
            embed.add_field(name="Temps:",value=f"\u2022 Récolte: {str(dr['temps_recolte']).removesuffix('.0')} minutes\n\u2022 Traitement: {str(dr['temps_traitement']).removesuffix('.0')} minutes\n\u2022 Vente: {str(tps).removesuffix('.0')} minutes",inline=False)

            view= customView(interaction,dr,b)

            await interaction.response.edit_message(content=f"<@!{interaction.user.id}>"+err,embed=embed,view=view)
        select.callback=select_cb
        view.add_item(select)
        embed=discord.Embed(title="Choix de la drogue à afficher",color=0x00ebeb)
        await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embed=embed,view=view)

    @app_commands.command(
        name="drogue-supprimer",
        description="supprime une drogue"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def drogue_supprimer(self,interaction:discord.Interaction,nom:str):
        try:
            database.supprimer_drog(nom=nom)
            await interaction.response.send_message(f"Drogue {nom} supprimée avec succès ! 🗑️")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"une erreur est survenue pendant la suppression de {nom}")

    @app_commands.command(
        name='drogue-vente-config',
        description="configure la vente de drogue"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def drogue_vente_config(self,interaction:discord.Interaction,type_de_drogue:str,temps_en_minutes:float,prix_qualite_aleatoire_1:float,prix_qualite_aleatoire_2:float,prix_qualite_aleatoire_3:float,prix_qualite_aleatoire_4:float):
        try:
            result=database.modifier_drog_vente(type_de_drogue,temps_vente=temps_en_minutes,prix_q1=prix_qualite_aleatoire_1,prix_q2=prix_qualite_aleatoire_2,prix_q3=prix_qualite_aleatoire_3,prix_q4=prix_qualite_aleatoire_4)
            if(result.matched_count>0):
                await interaction.response.send_message(f"la vente de {type_de_drogue} a été configurée")
            else:
                await interaction.response.send_message(f"la drogue {type_de_drogue} n'existe pas")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"une erreur est survenue pendant la configuration de la vente de {type_de_drogue}")
    
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
        name='vol',
        description="vol des items ou de l'argent à quelqu'un"
    )
    @app_commands.guild_only()
    async def vol(self,interaction:discord.Interaction,cible:discord.User):
        inv=database.get_inventaire(str(interaction.user.id))
        if(inv==None):
            await interaction.response.send_message(content="Vous ne possédez pas d'inventaire")
            return
        embed=discord.Embed(title="Vol",description="Choisissez ce que vous voulez voler à cette personne",color=0x00ebeb)
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
                r=random.random()
                if(r>proba):
                    if(selected=="Argent"):
                        if(database.retire_argent_liquide(str(cible.id),float(text.value))):
                            database.ajoute_argent_liquide(str(interaction.user.id),float(text.value))
                            await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] Vous avez réussi à voler {text.value.removesuffix('.0')}$ à <@!{cible.id}>. 🎉💸",color=0x00ebeb)
                        else:
                            await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] <@!{cible.id}> ne possède pas {text.value.removesuffix('.0')}$. 🎉💸",color=0xff0000)
                    else:
                        qtt=database.retirer_objet_inventaire(str(cible.id),selected,int(text.value))
                        database.ajouter_objet_inventaire(str(interaction.user.id),selected,int(qtt))
                        await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] Vous avez réussi à voler {qtt}{'g' if(' traitée' in objets['SAC_NOMS'][i]) else ''} {selected} à <@!{cible.id}>. 🎉💸")
                else:
                    if(selected=="Argent"):
                        await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] Vous n'avez pas réussi à voler {float(text.value)}$ à <@!{cible.id}>.")
                    else:
                        await interaction.response.edit_message(embed=None,view=None,content=f"[Notification] Vous n'avez pas réussi à voler {int(text.value)}{'g' if(' traitée' in objets['SAC_NOMS'][i]) else ''} {selected} à <@!{cible.id}>.")
            modal.add_item(text)
            modal.on_submit=on_submit
            await interaction.response.send_modal(modal)
        select.callback=select_cb
        view=discord.ui.View()
        view.add_item(select)
        await interaction.response.send_message(content=f"<@!{interaction.user.id}>",embed=embed,view=view)
    @app_commands.command(
        name="braquage-config",
        description="Permet de configurer un braquage."
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def braquage_config(self,interaction:discord.Interaction,type_braquage:str,montant_minimum:float=None,montant_maximum:float=None,temps_braquage:float=None):
        try:
            result=database.get_braq(type=type_braquage)
            if(result == None):
                if(type_braquage==None or montant_minimum==None or montant_maximum == None or temps_braquage == None):
                    await interaction.response.send_message(f"le type de braquage {type_braquage} n'existe pas veuillez entrer toutes les valeurs demandées")
                    return
                database.creer_braq(type_braquage,montant_minimum,montant_maximum,temps_braquage)
                await interaction.response.send_message(f"le type de braquage {type_braquage} a bien été créer")
            else:
                if(montant_minimum==None): montant_minimum = result["montant minimum"]
                if(montant_maximum==None): montant_maximum = result["montant maximum"]
                if(temps_braquage==None): temps_braquage = result["temps"]
                database.modifier_braq(type_braquage,montant_minimum,montant_maximum,temps_braquage)
                await interaction.response.send_message(f"le type de braquage {type_braquage} a bien été modifié")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"une erreur s'est produite pendant la création ou la modification du type de braquage: {type_braquage}")

    @app_commands.command(
        name="braquage-realiser",
        description="Permet de realiser un braquage."
    )    
    @app_commands.guild_only()
    async def braquage_realiser(self,interaction:discord.Interaction):
        joueur=interaction.user
        if(database.get_identite(str(joueur.id))==None):
            await interaction.response.send_message(content="Vous devez créer une identité avant d'effectuer un braquage")
        desc=""
        liste=[]
        braqs=list(database.get_braquages())
        for doc in braqs:
            desc+=f"**{doc['type']} :** entre {str(doc['montant minimum']).removesuffix('.0')} $ et {str(doc['montant maximum']).removesuffix('.0')} $, temps de braquage {str(doc['temps']).removesuffix('.0')} minutes\n"
            liste.append(discord.SelectOption(label=doc["type"],value=str(doc['type'])))
        file1=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
        file2=discord.File('images/braq.png',filename="braq.png")
        embed=discord.Embed(title="Braquage",description=desc,color=0x00ebeb)
        view=discord.ui.View()
        select=discord.ui.Select(options=liste)
        async def select_callback(interaction:discord.Interaction):
            selected=select.values[0]
            braq=database.get_braq(selected)
            timestamp=int((datetime.datetime.now()+datetime.timedelta(seconds=int(braq['temps']*60))).timestamp())
            msg=interaction.message
            embed=discord.Embed(title="Braquage",description=f"Le braquage de type {braq['type']} est en cours.\nMontant potentiel : {braq['montant minimum']}$ à {braq['montant maximum']}$.\nFin du braquage <t:{timestamp}:R>. \nLa police a été alertée.\n\u200b 🚨",color=0xff0000)
            embed.set_thumbnail(url='attachment://braq.png')
            embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            await interaction.response.edit_message(embed=embed,view=None)
            lspd_channel=interaction.guild.get_channel(int(os.getenv("LSPD_CHANNEL")))
            lspd_role=interaction.guild.get_role(int(os.getenv("LSPD_ID")))
            embed_lspd=discord.Embed(title="Braquage en cours",description=f"Un braquage est en cours\n\u2022 Type🏦: {braq['type']}\n\u2022 Auteur du braquage: <@!{joueur.id}>\n\u200b",color=0x00ebeb)
            file_lspd=discord.File('images/LSPD.png',filename="LSPD.png")
            file1=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            embed_lspd.set_thumbnail(url='attachment://LSPD.png')
            embed_lspd.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            await lspd_channel.send(files=[file1,file_lspd],embed=embed_lspd,content=f"<@${lspd_role}>")
            await asyncio.sleep(int(braq['temps']*60))
            montant=int(random.randrange(braq["montant minimum"],braq["montant maximum"])*100)/100
            embed_finis=discord.Embed(color=0x00ff00,title="Braquage terminé",description=f"Vous avez gagné {str(montant).removesuffix('.0')}$")
            database.ajoute_argent_liquide(str(interaction.user.id),montant)
            embed.set_thumbnail(url='attachment://braq.png')
            embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            await msg.edit(embed=embed_finis)
        select.callback=select_callback
        view.add_item(select)
        embed.set_thumbnail(url='attachment://braq.png')
        embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
        await interaction.response.send_message(files=[file1,file2],content=f"<@!{interaction.user.id}>",embed=embed,view=view)

async def setup(bot):
    await bot.add_cog(delit_commands_cog(bot))

    