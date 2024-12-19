from math import ceil
import os
import discord
from discord.ext import commands
from discord import app_commands
import databas as database

class Buttons(discord.ui.View):
        def __init__(self,liste_noms,liste_quantite,*,timeout=None):
            super().__init__(timeout=timeout or 180)
            self.liste_noms=liste_noms
            self.liste_prix=liste_quantite
            self.current_page=0
            self.max_page=self.get_max_page()
            
        def get_max_page(self):
            return int(ceil(len(self.liste_noms)/10))

        
        async def send_boutique(self,interaction):
            if(len(self.liste_noms)==0):
                embed=discord.Embed(title="Boutique:Supérette",description="la boutique est vide",color=0x00ebeb)
            else:
                embed=discord.Embed(title="Boutique:Supérette",description="\n\u200b",color=0x00ebeb)
                for i in range(10):
                    if(len(self.liste_noms)>i+10*self.current_page):
                        embed.add_field(name=f"Item: {self.liste_noms[i+10*self.current_page]}",value=f"\u25CF  Prix:{str(self.liste_prix[i+10*self.current_page]).removesuffix('.0')}$\n\u200b")
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            embed.set_footer(text=f"Realis RP \t\t\t\t\t\t\t\t\t\t      Page {self.current_page+1}/{self.max_page}",icon_url='attachment://logo_realis_rp_anime.gif')
            logo=discord.File('images/shop-get.png',filename="shop-get.png")
            embed.set_thumbnail(url='attachment://shop-get.png')
            await interaction.response.send_message(files=[logo,file_logo],
                                                    embed=embed,
                                                    content=f"<@!{interaction.user.id}>",
                                                    view=self,
                                                    )            
        async def send_affichage(self,interaction: discord.Interaction,button:discord.ui.button):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            if(len(self.liste_noms)==0):
                embed=discord.Embed(title="Boutique:Supérette",description="la boutique est vide",color=0x00ebeb)
            else:
                embed=discord.Embed(title="Boutique:Supérette",description="\n\u200b",color=0x00ebeb)
                for i in range(10):
                    if(len(self.liste_noms)>i+10*self.current_page):
                        embed.add_field(name=f"Item: {self.liste_noms[i+10*self.current_page]}",value=f"\u25CF  Prix:{str(self.liste_prix[i+10*self.current_page]).removesuffix('.0')}$\n\u200b")
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")
            embed.set_footer(text=f"Realis RP \t\t\t\t\t\t\t\t\t\t      Page {self.current_page+1}/{self.max_page}",icon_url='attachment://logo_realis_rp_anime.gif')
            logo=discord.File('images/shop-get.png',filename="shop-get.png")
            embed.set_thumbnail(url='attachment://shop-get.png')
            await interaction.response.edit_message(
                                                    attachments=[logo,file_logo],
                                                    embed=embed,
                                                    content=f"<@!{interaction.user.id}>",
                                                    view=self,
                                                    )

        @discord.ui.button(
            label="page précédente"
        )
        async def page_precedente(self,interaction: discord.Interaction,button:discord.ui.Button):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            if(self.current_page>0):
                self.current_page-=1
            await self.send_affichage(interaction,button)

        @discord.ui.button(
            label="page suivante"
        )
        async def page_suivante(self,interaction: discord.Interaction,button:discord.ui.Button):
            staff_role=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(self.base_interaction.user!=interaction.user and not staff_role in interaction.user.roles):
                return
            if(self.current_page<self.max_page-1):
                self.current_page+=1
            await self.send_affichage(interaction,button)


SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class boutique_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @app_commands.command(
        name='boutique-afficher',
        description='affiche la boutique'
    )    
    @app_commands.guild_only()
    async def boutique_afficher(self,interaction:discord.Interaction):
        objets=database.get_boutique()
        liste_objets_noms=[]
        liste_objets_prix=[]
        for obj in objets:
            liste_objets_noms.append(obj["nom"])
            liste_objets_prix.append(obj["prix"])
        
        view=Buttons(liste_objets_noms,liste_objets_prix)
        await view.send_boutique(interaction=interaction)

    def get_liste(self):
        boutique=database.get_boutique()
        l=[]
        for i in boutique:
            l.append(discord.SelectOption(label=i["nom"]+" : "+str(i["prix"]).removesuffix(".0")+"$",value=i["nom"]))
        return l
    
    @app_commands.command(
        name='boutique-acheter',
        description='acheter un item dans la boutique'
    )    
    @app_commands.guild_only()
    @app_commands.choices(methode=[
        app_commands.Choice(name="CB",value="cb"),
        app_commands.Choice(name="Liquide",value="liquide")
    ])
    async def boutique_acheter(self,interaction:discord.Interaction,methode:app_commands.Choice[str]):
        await interaction.response.defer()
        bi=interaction
        view=discord.ui.View()
        liste=self.get_liste()
        select=discord.ui.Select(options=liste,placeholder="Quel objet Acheter?")
        async def buttonPress(interaction:discord.Interaction):
            msg=interaction.message
            staff=interaction.guild.get_role(os.getenv("STAFF_ID"))
            if(interaction.user!=bi.user and not staff in interaction.user.roles):
                return
            modal=discord.ui.Modal(title="Quelle quantité voulez vous?")
            text=discord.ui.TextInput(
                label='Quantité',
                placeholder='Quantité souhaitée',
            )
            async def on_submit(interaction: discord.Interaction):
                await interaction.response.defer()
                try:
                    nom_item=select.values[0]
                    quantite=int(str(text))
                    item=database.get_item(nom_item)
                    if(item!=None):
                        prix=item["prix"]*quantite
                        if(methode.value=="cb"):
                            if(database.get_compte_bancaire(str(interaction.user.id))!=None):
                                if(database.retire_argent_banque(str(interaction.user.id),prix)):
                                    database.ajouter_objet_inventaire(str(interaction.user.id),nom_item,quantite)
                                    database.cree_transaction(str(interaction.user.id),"Achat",prix)
                                    await interaction.followup.edit_message(message_id=msg.id,content=f"<@!{interaction.user.id}> achat de {quantite} {nom_item} pour {str(prix).removesuffix('.0')}$ par cb effectué",view=None)
                                else:
                                    await interaction.followup.edit_message(message_id=msg.id,content=f"<@!{interaction.user.id}> vous n'avez pas assez d'argent en banque pour acheter cet objet",view=None)
                            else:
                                await interaction.followup.edit_message(message_id=msg.id,content=f"<@!{interaction.user.id}> vous ne possédez pas de compte bancaire",view=None)
                        if(methode.value=="liquide"):
                            if(database.retire_argent_liquide(str(interaction.user.id),prix)):
                                database.ajouter_objet_inventaire(str(interaction.user.id),nom_item,quantite)
                                await interaction.followup.edit_message(message_id=msg.id,content=f"<@!{interaction.user.id}> achat de {quantite} {nom_item} pour {str(prix).removesuffix('.0')}$ en liquide effectué",view=None)
                            else:
                                await interaction.followup.edit_message(message_id=msg.id,content=f"<@!{interaction.user.id}> vous n'avez pas assez d'argent liquide pour acheter cet objet",view=None)
                
                except Exception as e:
                    print(e)
                    pass
            modal.add_item(text)
            modal.on_submit=on_submit
            await interaction.response.send_modal(modal)
        select.callback=buttonPress
        view.add_item(select)
        await interaction.followup.send(f"Quel item voulez vous acheter?",view=view)

    @app_commands.command(
        name='inventaire',
        description="affiche l'inventaire"
    )    
    @app_commands.guild_only()
    async def inventaire(self,interaction:discord.Interaction,joueur:discord.User=None):
        try:
            if(joueur==None): joueur=interaction.user
            inventaire=database.get_inventaire(str(joueur.id))
            embed=discord.Embed(title=f"Inventaire de {joueur.display_name}",color=0x00ebeb)
            text="\u2022 **carte identité** - 1x "
            ppa=inventaire["permis_port_arme"]
            pc=inventaire["permis_conduire"]
            if(ppa):
                text+="\n\u2022 **permis port d'arme** - 1x "
            if(pc):
                text+="\n\u2022 **permis de conduire** - 1x "
            embed.add_field(name="🪪 \u2022 portefeuille",value=text,inline=False)
            noms_objets=inventaire["SAC_NOMS"]
            quantites_objets=inventaire["SAC_QUANTITE"]
            if(len(noms_objets)==0):
                items="Vous n'avez rien dans votre sac à dos"
            else:
                items=""
                for i in range(len(noms_objets)):
                    items+=f"\n\u2022 **{noms_objets[i]}** - {quantites_objets[i]}"+("g" if(" traitée" in noms_objets[i]) else "x")
            embed.add_field(name="🎒 \u2022 Sac à dos",value=items,inline=False)
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")

            embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            embed.set_thumbnail(url=joueur.display_avatar.url)
            
            await interaction.response.send_message(file=file_logo,embed=embed)
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"ne peux pas afficher l'inventaire de <@!{joueur.id}>")
    @app_commands.command(
        name='fouiller',
        description="fouiller un joueur l'inventaire"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role('Staff','lspd')
    async def fouiller(self,interaction:discord.Interaction,cible:discord.User):
        try:
            if(cible==None): cible=interaction.user
            inventaire=database.get_inventaire(str(cible.id))
            embed=discord.Embed(title=f"Inventaire de {cible.display_name}",color=0x00ebeb)
            text="\u25CF **carte identité** - 1x "
            ppa=inventaire["permis_port_arme"]
            pc=inventaire["permis_conduire"]
            if(ppa):
                text+="\n\u25CF **permis port d'arme** - 1x "
            if(pc):
                text+="\n\u25CF **permis de conduire** - 1x "
            embed.add_field(name="🪪 \u25CFportefeuille",value=text,inline=False)
            noms_objets=inventaire["SAC_NOMS"]
            quantites_objets=inventaire["SAC_QUANTITE"]
            if(len(noms_objets)==0):
                items="rien ne se trouve dans son sac à dos"
            else:
                items=""
                for i in range(len(noms_objets)):
                    items+=f"\n\u25CF **{noms_objets[i]}** - {quantites_objets[i]}x"
            embed.add_field(name="🎒 \u25CFSac à dos",value=items,inline=False)
            file_logo=discord.File('images/logo_realis_rp_anime.gif',filename="logo_realis_rp_anime.gif")

            embed.set_footer(text='Realis RP',icon_url='attachment://logo_realis_rp_anime.gif')
            await interaction.response.send_message(file=file_logo,embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"ne peux pas afficher l'inventaire de <@!{cible.id}>")

    @app_commands.command(
        name='objet-utiliser',
        description="utiliser un objet"
    )    
    @app_commands.guild_only()
    async def objet_utiliser(self,interaction:discord.Interaction,nom_item:str,quantite:int):
        try:
            if(database.retirer_objet_inventaire(str(interaction.user.id),nom_item,quantite)!=-1):
                await interaction.response.send_message(f"<@!{interaction.user.id}> vous avez utiliser {quantite} {nom_item}")
            else:
                await interaction.response.send_message(f"<@!{interaction.user.id}> vous ne pouvez pas utiliser cet objet")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"<@!{interaction.user.id}> vous ne pouvez pas utiliser cet objet")

    @app_commands.command(
        name='objet-donner',
        description="donner un objet"
    )    
    @app_commands.guild_only()
    async def objet_donner(self,interaction:discord.Interaction,nom_item:str,quantite:int,destinataire:discord.User):
        try:
            if(database.retirer_objet_inventaire2(str(interaction.user.id),nom_item,quantite)):
                database.ajouter_objet_inventaire(str(destinataire.id),nom_item,quantite)
                await interaction.response.send_message(f"<@!{interaction.user.id}> vous avez donner {quantite} {nom_item} à <@!{destinataire.id}>")
            else:
                await interaction.response.send_message(f"<@!{interaction.user.id}> vous ne pouvez pas donner {quantite} {nom_item} à <@!{destinataire.id}>")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"<@!{interaction.user.id}> vous ne pouvez pas donner {quantite} {nom_item} à <@!{destinataire.id}>")
    
    @app_commands.command(
        name='boutique-ajout',
        description="ajoute un objet dans la boutique"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def boutique_ajout(self,interaction:discord.Interaction,nom_item:str,prix:float):
        try:
            database.ajouter_objet_boutique(nom_item,prix)
            await interaction.response.send_message(f"l'item {nom_item} a bien été ajouté à la boutique ✅")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"l'item {nom_item} n'a pas pu être ajouté")

    @app_commands.command(
        name='boutique-modifie',
        description="modifie un objet dans la boutique"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def boutique_modifier(self,interaction:discord.Interaction,nom_item:str,prix:float):
        try:
            database.modifier_objet_boutique(nom_item,prix)
            await interaction.response.send_message(f"l'item {nom_item} a bien été modifié ✅")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"l'item {nom_item} n'a pas pu être modifié")


    @app_commands.command(
        name='boutique-modifie-nom',
        description="modifie le nom d'un objet dans la boutique"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def boutique_modifie_nom(self,interaction:discord.Interaction,nom_item:str,nouveau_nom:str):
        try:
            database.modifier_nom_objet_boutique(nom_item,nouveau_nom)
            await interaction.response.send_message(f"l'item {nom_item} a bien été modifié dans la boutique ✅")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"l'item {nom_item} n'a pas pu être modifié")

    @app_commands.command(
        name='boutique-retirer',
        description="retire un objet dans la boutique"
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_role('Staff')
    async def boutique_retirer(self,interaction:discord.Interaction,nom_item:str,nouveau_nom:str):
        try:
            database.retirer_objet_boutique(nom_item)
            await interaction.response.send_message(f"l'item {nom_item} a bien été retiré de la boutique ✅")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"l'item {nom_item} n'a pas pu être retiré")

async def setup(bot):
    await bot.add_cog(boutique_commands_cog(bot))