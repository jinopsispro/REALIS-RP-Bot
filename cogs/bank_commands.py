import io
import os
import discord
from discord.ext import commands
from discord import app_commands
import databas as database
from PIL import ImageDraw
from PIL import Image
from PIL import ImageFont

SERVER_ID = os.getenv('SERVER_ID')
@app_commands.guilds(discord.Object(id = SERVER_ID))
class bank_commands_cog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @app_commands.command(
        name='compte-bancaire-creer',
        description='cree compte bancaire'
    )    
    @app_commands.guild_only()
    @app_commands.checks.has_any_role(int(os.getenv("STAFF_ID")),int(os.getenv("BANQUIER_ID")))
    async def compte_bancaire_creer(self,interaction:discord.Interaction,joueur:discord.User):
        try:
            if(not database.cree_compte_bancaire(str(joueur.id))):
                await interaction.response.send_message(f"<@!{joueur.id}> ne possède pas de carte d'identité")
                return
            database.ajoute_argent_banque(str(joueur.id),5000)
            await interaction.response.send_message(f"le compte bancaire pour <@!{joueur.id}> a été créé")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"le compte bancaire n'a pas pu être créé?")

    def create_image_bank(self,solde,cash,identite,transactions):
        img = Image.open("images\\compte_bancaire.png")
        fontForImg = ImageFont.truetype("arial.ttf", 24, encoding="unic")
        draw = ImageDraw.Draw(img)
        draw.text((50, 150),f"{str(solde['solde']).removesuffix('.0')}$",(0,0,0),font=fontForImg)
        draw.text((285, 150),f"{str(cash['cash']).removesuffix('.0')}$",(0,0,0),font=fontForImg)
        draw.text((145, 360),f"{identite['nom']}",(0,0,0),font=fontForImg)
        draw.text((175, 450),f"{identite['prenom']}",(0,0,0),font=fontForImg)
        draw.text((240, 541),"1850XXXXXXXXXXXX",(0,0,0),font=fontForImg)
        j=len(transactions)-1
        for i in range(min(8,len(transactions))):
            couleur="lightgray"
            t=transactions[j]
            texte=t["type_transaction"]
            if(t["type_transaction"]=="Virement"):
                dest_id=database.get_compte_bancaire_from_id(t['num_compte_destination'])['id_identite']
                dest=database.get_identite_from_id(dest_id)
                source_id=database.get_compte_bancaire_from_id(t['num_compte_source'])['id_identite']
                source=database.get_identite_from_id(source_id)
                if(source_id==identite["_id"]):
                    couleur="red"
                    texte=f"- {str(t['montant']).removesuffix('.0')}$ (Paiement à {dest['nom']} {dest['prenom']})"
                else:
                    couleur="green"
                    texte=f"+ {str(t['montant']).removesuffix('.0')}$ (Paiement de {source['nom']} {source['prenom']}) "

                    
            if(t["type_transaction"]=="Ouverture"):
                couleur="green"
                texte=f"+ 5000$ (Ouverture du compte)"
            if(t["type_transaction"]=="Ajouter"):
                couleur="green"
                texte=f"+ {str(t['montant']).removesuffix('.0')}$ (Paiement du Gouvernement)"
            if(t["type_transaction"]=="Supprimer"):
                couleur="red"
                texte=f"- {str(t['montant']).removesuffix('.0')}$ (Retrait du Gouvernement)"
            if(t["type_transaction"]=="Deposer"):
                couleur="green"
                texte=f"+ {str(t['montant']).removesuffix('.0')}$ (dépot d'argent)"
            if(t["type_transaction"]=="Retirer"):
                couleur="red"
                texte=f"- {str(t['montant']).removesuffix('.0')}$ (retrait d'argent)"
            if(t["type_transaction"]=="Achat"):
                couleur="red"
                texte=f"- {str(t['montant']).removesuffix('.0')}$ (achat superette)"
            draw.text((655, 130+i*60), text=texte, font=fontForImg,fill=couleur)
            j-=1
        if(len(transactions)>9):
            draw.text((655,600), text="...", font=fontForImg,fill="black")
        return img

    @app_commands.command(
        name='compte-bancaire-afficher',
        description='affiche compte bancaire'
    )    
    @app_commands.guild_only()
    async def compte_bancaire_afficher(self,interaction:discord.Interaction,joueur:discord.User=None):
        if(joueur==None):
            joueur=interaction.user
        if(database.get_compte_bancaire(str(joueur.id))==None):
            if(interaction.user.id ==joueur.id):
                await interaction.response.send_message(f"<@!{joueur.id}> ne possède pas de compte bancaire")
                return
            await interaction.response.send_message(f"<@!{interaction.user.id}>: <@!{joueur.id}> ne possède pas de compte bancaire")
            return
        solde=database.get_argent_banque(str(joueur.id))
        cash=database.get_argent_liquide(str(joueur.id))
        identite=database.get_identite(str(joueur.id))
        transactions=database.get_transactions(str(joueur.id))
        image=self.create_image_bank(solde,cash,identite,list(transactions))
        image_file=None
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            image_file=discord.File(fp=image_binary, filename='image.png')
        await interaction.response.send_message(file=image_file,content=f"<@!{joueur.id}>")

    @app_commands.command(
        name='payer',
        description='payer un joueur'
    )
    @app_commands.guild_only()
    @app_commands.choices(moyen_paiement=[
        app_commands.Choice(name="Liquide",value="liquide"),
        app_commands.Choice(name="Virement",value="virement")
    ])
    async def payer(self,interaction:discord.Interaction,destinataire:discord.User,moyen_paiement:app_commands.Choice[str],montant:float,description:str="\u200b"):
        try:
            if(moyen_paiement.value=="liquide"):
                database.retire_argent_liquide(str(interaction.user.id),montant)
                database.ajoute_argent_liquide(str(destinataire.id),montant)
            if(moyen_paiement.value=="virement"):
                if(database.get_compte_bancaire(str(interaction.user.id))!=None and database.get_compte_bancaire(str(destinataire.id))!=None):
                    database.retire_argent_banque(str(interaction.user.id),montant)
                    database.ajoute_argent_banque(str(destinataire.id),montant)
                    database.cree_transaction(str(interaction.user.id),"Virement",montant,description,str(destinataire.id))
                    await interaction.response.send_message(f"<@!{interaction.user.id}>Le paiement par virement de {str(montant).removesuffix('.0')}$ à <@!{destinataire.id}> a bien été effectué")
                else:
                    await interaction.response.send_message(f"<@!{interaction.user.id}> votre paiement n'a pas pu être effectué, vous ou le destinataire ne possède pas de compte bancaire.")
        except Exception as e:
            print(e)
            await interaction.response.send_message("Une erreur est survenu pendant le paiement")        
    
    @app_commands.command(
        name='retirer',
        description="retirer de l'argent de votre compte en banque"
    )
    @app_commands.guild_only()
    async def retirer(self,interaction:discord.Interaction,montant:float):
        try:
            if(database.get_compte_bancaire(str(interaction.user.id))!=None):
                database.retire_argent_banque(str(interaction.user.id),montant)
                database.ajoute_argent_liquide(str(interaction.user.id),montant)
                database.cree_transaction(str(interaction.user.id),"Retirer",montant)
                await interaction.response.send_message(f"<@!{interaction.user.id}> a retirer {str(montant).removesuffix('.0')}$")
            else:
                await interaction.response.send_message(f"<@!{interaction.user.id}> n'a pas pu retirer d'argent")
        except Exception as e:
            print(e)
            await interaction.response.send_message(f"<@!{interaction.user.id}> vous ne possédez pas de compte bancaire")

    @app_commands.command(
        name='déposer',
        description="déposer de l'argent sur votre compte en banque"
    )
    @app_commands.guild_only()
    async def deposer(self,interaction:discord.Interaction,montant:float):
        try:
            if(database.get_compte_bancaire(str(interaction.user.id))!=None):
                database.retire_argent_liquide(str(interaction.user.id),montant)
                database.ajoute_argent_banque(str(interaction.user.id),montant)
                database.cree_transaction(str(interaction.user.id),"Deposer",montant)
                await interaction.response.send_message(f"<@!{interaction.user.id}> a deposer {str(montant).removesuffix('.0')}$")
            else:
                await interaction.response.send_message(f"<@!{interaction.user.id}> vous ne possédez pas de compte bancaire")

        except Exception as e:
            print(e)
            await interaction.response.send_message(f"<@!{interaction.user.id}> n'a pas pu déposer d'argent")

    @app_commands.command(
        name='argent-ajouter',
        description="ajoute de l'argent"
    )
    @app_commands.guild_only()
    @app_commands.choices(destination=[
        app_commands.Choice(name="Banque",value="banque"),
        app_commands.Choice(name="Cash",value="cash")
    ])
    @app_commands.checks.has_role(int(os.getenv("STAFF_ID")))
    async def argent_ajouter(self,interaction:discord.Interaction,destination:app_commands.Choice[str],montant:float,joueur:discord.User,raison:str="\u200b"):
        if((joueur == None)):
            await interaction.response.send_message("vous devez choisir un joueur")
            return
        
        if(destination.value=="banque"):
            try:
                database.ajoute_argent_banque(str(joueur.id),montant)
                database.cree_transaction(str(joueur.id),"Ajouter",montant)
                await interaction.response.send_message(f"💳   Vous avez bien ajouté {str(montant).removesuffix('.0')}$ au compte en banque de <@!{joueur.id}> !")
            except:
                await interaction.response.send_message(f"<@!{joueur.id}> ne possède pas de compte bancaire\n")
        if(destination.value=="cash"):
            try:
                database.ajoute_argent_liquide(str(joueur.id),montant)
                await interaction.response.send_message(f"💰   Vous avez bien ajouté {str(montant).removesuffix('.0')}$ en cash à  <@!{joueur.id}> !")
            except Exception as e:
                print (e)
                await interaction.response.send_message(f"<@!{joueur.id}> ne peut pas recevoir d'argent en cash\n")
    
    @app_commands.command(
        name='argent-ajouter-role',
        description="ajoute de l'argent à tous les joueurs ayant le role"
    )
    @app_commands.guild_only()
    @app_commands.choices(destination=[
        app_commands.Choice(name="Banque",value="banque"),
        app_commands.Choice(name="Cash",value="cash")
    ])
    @app_commands.checks.has_role(int(os.getenv("STAFF_ID")))
    async def argent_ajouter_role(self,interaction:discord.Interaction,destination:app_commands.Choice[str],montant:float,role:discord.Role,raison:str="\u200b"):
        if((role == None)):
            await interaction.response.send_message("vous devez choisir un role")
            return
        if(destination.value=="banque"):
            try:
                for joueur in role.members:
                    if(database.get_compte_bancaire(str(joueur.id))!=None):
                        database.ajoute_argent_banque(str(joueur.id),montant)
                        database.cree_transaction(str(joueur.id),"Ajouter",montant,raison)
                await interaction.response.send_message(f"💳   Vous avez bien ajouté {str(montant).removesuffix('.0')}$ aux comptes en banque des joueurs possédant le rôle <@&{role.id}> !")
            except:
                await interaction.response.send_message(f"erreur pendant l'ajout d'argent\n")
        if(destination.value=="cash"):
            try:
                for joueur in role.members:
                    if(database.get_inventaire(str(joueur.id))!=None):
                        database.ajoute_argent_liquide(str(joueur.id),montant)
                await interaction.response.send_message(f"💰   Vous avez bien ajouté {str(montant).removesuffix('.0')}$ en cash aux joueur possédant le role <@&{role.id}> !")
            except:
                await interaction.response.send_message(f"erreur pendant l'ajout d'argent\n")
     

    @app_commands.command(
        name='argent-retirer',
        description="retirer de l'argent"
    )
    @app_commands.guild_only()
    @app_commands.choices(destination=[
        app_commands.Choice(name="Banque",value="banque"),
        app_commands.Choice(name="Cash",value="cash")
    ])
    @app_commands.checks.has_role(int(os.getenv("STAFF_ID")))
    async def argent_retirer(self,interaction:discord.Interaction,destination:app_commands.Choice[str],montant:float,joueur:discord.User=None,role:discord.Role=None):
        if((joueur != None and role != None)or(joueur==None and role == None)):
            await interaction.response.send_message("vous devez choisir un rôle ou joueur, un seul parmi les deux")
        if(joueur!=None):
            if(destination.value=="banque"):
                try:
                    database.retire_argent_banque(str(joueur.id),montant)                        
                    database.cree_transaction(str(joueur.id),"Supprimer",montant)
                    await interaction.response.send_message(f"💳   Vous avez bien enlever {str(montant).removesuffix('.0')}$ au compte en banque de <@!{joueur.id}> !")
                except Exception as e:
                    print(e)
                    await interaction.response.send_message(f"<@!{joueur.id}> ne possède pas de compte bancaire\n")
            if(destination.value=="cash"):
                try:
                    database.retire_argent_liquide(str(joueur.id),montant)
                    await interaction.response.send_message(f"💰   Vous avez bien enlever {str(montant).removesuffix('.0')}$ en cash à  <@!{joueur.id}> !")
                except Exception as e:
                    print(e)
                    await interaction.response.send_message(f"<@!{joueur.id}> ne peut pas recevoir d'argent en cash\n")
        if(role!=None):
            if(destination.value=="banque"):
                for joueur_role in role.members:
                    try:
                        database.ajoute_argent_banque(joueur_role.id,montant)
                        database.cree_transaction(str(joueur_role.id),"Ajouter",montant)
                    except:
                        pass
                await interaction.response.send_message(f"💳   Vous avez bien retirer {str(montant).removesuffix('.0')}$ au compte en banque des joueurs ayant le rôle <@&{role.id}> !")
            if(destination.value=="cash"):
                for joueur_role in role.members:
                    try:
                        database.ajoute_argent_liquide(str(joueur.id),montant)
                    except:
                        pass
                await interaction.response.send_message(f"💰   Vous avez bien retirer {str(montant).removesuffix('.0')}$ en cash aux joueurs ayant le rôle <@&{role.id}> !")

async def setup(bot):
    await bot.add_cog(bank_commands_cog(bot))
    