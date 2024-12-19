from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import datetime

uri=os.getenv("DB_CONNEXION")
client= MongoClient(uri,server_api=ServerApi('1'))

try:
    client.admin.command('ping')
except Exception as e:
    print(e)

db = client.tests

def get_id(discord_id:str):
    '''
    renvoie les id d'identité à partir de celui de discord
    '''
    id_list= db.identite.find_one({"id_discord": discord_id},{'_id':1})
    return id_list
    
def get_compte_bancaire_from_id(id_identite):
    id_obj=ObjectId(id_identite)
    return db.compte_bancaire.find_one({"_id":id_obj})

def get_compte_bancaire(discord_ID:str):
    '''
    renvoie les comptes bancaires liés à l'id discord associé
    avec en premier élément l'état de la recherche
    -1 si trouvé un compte mais plusieurs identités
    0 si trouvé un compte
    '''
    ids=get_id(discord_id=discord_ID)
    if(ids==None):
        return None
    compte=db.compte_bancaire.find_one({"id_identite":ids["_id"]})
    return compte

def cree_compte_bancaire(discord_ID:str):
    '''
    cree un compte bancaire lié à l'id discord associé
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return False
    id=ids["_id"]
    db.compte_bancaire.insert_one(
        {
            "id_identite":id,
            "solde":0.0
    })
    cree_transaction(discord_ID,"Ouverture")
    return True

def supprime_compte_bancaire(discord_ID:str):
    ids=get_id(discord_ID)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.compte_bancaire.delete_many({"id_discord":ids["_id"]})

def cree_identite(discord_ID:str,prenom,nom,genre,jour,mois,annee,lieu_naissance,nationalite):
    '''
    cree une identite avec les informations associées
    '''
    db.identite.insert_one(
        {
            "id_discord":discord_ID,
            "nom":nom,
            "prenom":prenom,
            "genre":genre,
            "date_de_naissance":datetime.datetime(annee,mois,jour,0,0,0),
            "lieu_de_naissance":lieu_naissance,
            "nationalite":nationalite,

            "permis_voiture" : False,
            "permis_moto" : False,
            "permis_camion" : False,
            "permis_bateau" : False,
            "permis_avion" : False,
            "permis_helicoptere" : False,

            "permis_arme_legere" : False,
            "permis_arme_lourde" : False,
            "permis_arme_blanche" : False
    })
def get_identite_from_id(id:str):
    id_obj=ObjectId(id)
    identites = db.identite.find_one({"_id":id_obj})
    return identites

def get_identite(discord_ID:str):
    '''
    retourne les infos sur l'identité du joueur
    '''
    identites = db.identite.find_one({"id_discord": discord_ID})
    return identites
def find_identite(nom:str,prenom:str):
    '''
    trouve une identite a partir du nom et du prenom
    '''
    identites=db.identite.find({"nom":nom,"prenom":prenom})
    return identites

def supprime_identites(discord_ID:str):
    '''
    supprime toutes les identités du joueur
    '''
    try:
        q=db.identite.delete_many({"id_discord": discord_ID})
    except Exception as e:
        raise e
    

def cree_carte_grise(discord_ID:str,immatriculation,modele):
    '''
    cree une carte grise avec les informations associées
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return False
    id=ids["_id"]
    db.carte_grise.insert_one({
        "id_identite" : id,
        "modele" : modele,
        "immatriculation" : immatriculation,
        "date_circulation":datetime.datetime.now()
    })
    return True

def modifie_carte_grise(discord_ID:str,immatriculation,modele):
    '''
    modifie la carte grise liée à l'immatriculation
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return False
    id=ids["_id"]
    db.carte_grise.update_one({"immatriculation":immatriculation},{"$set",
        {
        "id_identite" : id,
        "modele" : modele
        }
    })
    return True

def get_carte_grise_joueur(discord_ID:str):
    '''
    Retourne les infos des cartes grises du joueur
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return None
    carte_grises=db.carte_grise.find({'id_identite':ids["_id"]})
    return carte_grises

def get_carte_grise_immat(immatriculation):
    '''
    retourne les infos de carte grise lié à l'immatriculation
    '''
    carte_grises=db.carte_grise.find_one({'immatriculation':immatriculation})
    return carte_grises

def get_carte_grise_immat_joueur(discord_ID:str,immatriculation):
    ids=get_id(discord_ID)
    if(ids==None):
        return None
    carte_grises=db.carte_grise.find({'id_identite':ids["_id"],'immatriculation':immatriculation})
    return carte_grises

def supprime_carte_grise_joueur(discord_ID:str):
    '''
    supprime les infos des cartes grises du joueur
    '''
    try:
        ids=get_id(discord_ID)
        if(ids==None):
            raise NameError("ne possède pas d'id")
        db.carte_grise.delete_many({"id_identite":ids["_id"]})
    except Exception as e:
        print(e)
        raise e
    
def supprime_carte_grise(immatriculation):
    '''
    supprime les infos de la carte grise
    '''
    try:
        db.carte_grise.delete_one({"immatriculation":immatriculation})
        return True
    except Exception as e:
        print(e)
        return False
    


def cree_permis_de_conduire(discord_ID:str,type):
    '''
    ajoute un permis de conduire à un joueur
    si joueur ne possède pas la carte de permis de conduire dans l'invetaire, l'ajoute
    '''
    if(type==None):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_voiture":True,
                "permis_moto":True,
                "permis_camion":True,
                "permis_bateau":True,
                "permis_avion":True,
                "permis_helicoptere":True,
                "date_permis_voiture":datetime.datetime.now(),
                "date_permis_moto":datetime.datetime.now(),
                "date_permis_camion":datetime.datetime.now(),
                "date_permis_bateau":datetime.datetime.now(),
                "date_permis_avion":datetime.datetime.now(),
                "date_permis_helicoptere":datetime.datetime.now()
            }}
            ,upsert=False)
        return result.matched_count>0
    if(type=="voiture"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_voiture":True,
                "date_permis_voiture":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="moto"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_moto":True,
                "date_permis_moto":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="camion"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_camion":True,
                "date_permis_camion":datetime.datetime.now()
            }}
            ,upsert=False) 
        return result.matched_count>0 
    if(type=="bateau"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_bateau":True,
                "date_permis_bateau":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="avion"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_avion":True,
                "date_permis_avion":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="helicoptere"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_helicoptere":True,
                "date_permis_helicoptere":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    
def get_permis_de_conduire(discord_ID:str,type=None):
    '''
    renvoie les infos de permis de conduire du joueur correspondant
    '''
    if(type==None):
        return db.identite.find_one({"id_discord":discord_ID},{"nom":1,"prenom":1,"date_de_naissance":1,"permis_voiture":1,"permis_moto":1,"permis_camion":1,"permis_bateau":1,"permis_avion":1,"permis_helicoptere":1,"date_permis_voiture":1,"date_permis_moto":1,"date_permis_camion":1,"date_permis_avion":1,"date_permis_helicoptere":1,"date_permis_bateau":1})
    if(type=="voiture"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_voiture":1,"date_permis_voiture":1})
    if(type=="moto"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_moto":1,"date_permis_moto":1})
    if(type=="camion"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_camion":1,"date_permis_camion":1})
    if(type=="bateau"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_bateau":1,"date_permis_bateau":1})
    if(type=="avion"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_avion":1,"date_permis_avion":1})
    if(type=="helicoptere"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_helicoptere":1,"date_permis_helicoptere":1})
    raise RuntimeError("valeur de la variable type non valide")

def retire_permis_conduire(discord_ID:str,type):
    '''
    retire un permis de conduire
    si plus aucun permis: retire carte permis de l'inventaire
    '''
    if(type==None):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_voiture":False,
                "permis_moto":False,
                "permis_camion":False,
                "permis_bateau":False,
                "permis_avion":False,
                "permis_helicoptere":False,
                "date_permis_voiture":datetime.datetime.min,
                "date_permis_moto":datetime.datetime.min,
                "date_permis_camion":datetime.datetime.min,
                "date_permis_bateau":datetime.datetime.min,
                "date_permis_avion":datetime.datetime.min,
                "date_permis_helicoptere":datetime.datetime.min
            }}
            ,upsert=False)
        return result.matched_count>0
    if(type=="voiture"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_voiture":False,
                "date_permis_voiture":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="moto"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_moto":False,
                "date_permis_moto":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="camion"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_camion":False,
                "date_permis_camion":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="bateau"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_bateau":False,
                "date_permis_bateau":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="avion"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_avion":False,
                "date_permis_avion":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="helicoptere"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_helicoptere":False,
                "date_permis_helicoptere":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
        
def cree_permis_port_arme(discord_ID:str,type=None):
    '''
    ajoute un permis de port d'arme au joueur
    '''
    if(type==None):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_blanche":True,
                "permis_arme_legere":True,
                "permis_arme_lourde":True,
                "date_permis_lourde":datetime.datetime.now(),
                "date_permis_legere":datetime.datetime.now(),
                "date_permis_blanche":datetime.datetime.now(),

            }}
            ,upsert=False)
        return result.matched_count>0
    if(type=="lourde"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_lourde":True,
                "date_permis_lourde":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="legere"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_legere":True,
                "date_permis_legere":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="blanche"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_blanche":True,
                "date_permis_blanche":datetime.datetime.now()
            }}
            ,upsert=False)  
        return result.matched_count>0

def add_permis_inventaire(discord_id:str):
    ids=get_id(discord_id)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.update_one(
        {
            "id_identite":ids["_id"]
        },{"$set":
           {
                "permis_port_arme":True
           }
        }
    )

def remove_permis_inventaire(discord_id:str):
    ids=get_id(discord_id)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.update_one(
        {
            "id_identite":ids["_id"]
        },{"$set":
           {
                "permis_port_arme":False        
            }
        }
    )
def add_permis_conduire_inventaire(discord_id:str):
    ids=get_id(discord_id)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.update_one(
        {
            "id_identite":ids["_id"]
        },{"$set":
           {
                "permis_conduire":True
           }
        }
    )

def remove_permis_conduire_inventaire(discord_id:str):
    ids=get_id(discord_id)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.update_one(
        {
            "id_identite":ids["_id"]
        },{"$set":
           {
                "permis_conduire":False
           }
        }
    )

def get_permis_port_arme(discord_ID:str,type=None):
    '''
    renvoie les infos d'un permis de port d'arme du joueur
    '''
    if(type==None):
        return db.identite.find_one({"id_discord":discord_ID},{"nom":1,"prenom":1,"permis_arme_legere":1,"permis_arme_lourde":1,"permis_arme_blanche":1,"date_permis_lourde":1,"date_permis_legere":1,"date_permis_blanche":1})
    if(type=="lourde"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_arme_legere":1,"date_permis_legere":1})
    if(type=="legere"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_arme_lourde":1,"date_permis_lourde":1})
    if(type=="blanche"):
        return db.identite.find_one({"id_discord":discord_ID},{"permis_arme_blanche":1,"date_permis_blanche":1})
    raise RuntimeError("valeur de la variable type non valide")

def retire_permis_port_arme(discord_ID:str,type=None):
    '''
    retire un permis de port d'arme au joueur
    '''
    if(type==None):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_blanche":False,
                "permis_arme_legere":False,
                "permis_arme_lourde":False,
                "date_permis_lourde":datetime.datetime.min,
                "date_permis_legere":datetime.datetime.min,
                "date_permis_blanche":datetime.datetime.min
            }}
            ,upsert=False)
        return result.matched_count>0
    if(type=="lourde"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_lourde":False,
                "date_permis_lourde":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="legere"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_legere":False,
                "date_permis_legere":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    if(type=="blanche"):
        result=db.identite.update_one({"id_discord":discord_ID},
            {"$set":{
                "permis_arme_blanche":False,
                "date_permis_blanche":datetime.datetime.min
            }}
            ,upsert=False)  
        return result.matched_count>0
    

def ajoute_argent_liquide(discord_ID:str,montant):
    '''
    ajoute un montant d'argent liquide à un joueur
    '''
    ids=get_id(discord_id=discord_ID)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.update_one({"id_identite":ids["_id"]},{"$inc":{"cash":montant}})

def get_argent_liquide(discord_ID:str):
    '''
    retourne l'argent liquide contenu dans le sac
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return None
    return db.Inventaire.find_one({"id_identite":ids["_id"]},{"cash":1})

def retire_argent_liquide(discord_ID:str,montant):
    '''
    retire un montant d'argent liquide à un joueur
    '''
    if(get_argent_liquide(discord_ID)["cash"] - montant>=0):
        ajoute_argent_liquide(discord_ID,-montant)
        return True
    else :
        return False

def ajoute_argent_banque(discord_ID:str,montant):
    '''
    ajoute un montant d'argent en banque à un joueur
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.compte_bancaire.update_one({"id_identite":ids["_id"]},{"$inc":{"solde":montant}})


def get_argent_banque(discord_ID:str):
    '''
    retourne l'argent contenu en banque
    '''    
    id=get_id(discord_ID)
    if(id==None):
        return None
    return db.compte_bancaire.find_one({"id_identite":id["_id"]},{"solde":1})
def retire_argent_banque(discord_ID:str,montant):
    '''
    retire un montant d'argent en banque à un joueur
    '''
    if(get_argent_banque(discord_ID)["solde"] - montant>=0):
        ajoute_argent_banque(discord_ID,-montant)
        return True
    else :
        return False

def cree_transaction(discord_id_source:str,type_transaction,montant=0.0,description_transaction="\u200b",discord_id_destination=None):
    try:
        id_compte_source=get_compte_bancaire(discord_id_source)["_id"]
    except StopIteration:
        raise(ValueError("pas de compte source!"))
    if(discord_id_destination!=None):
        try:
            id_compte_destination=get_compte_bancaire(discord_id_destination)["_id"]
        except StopIteration:
            raise(ValueError("pas de compte destination!"))

        db.Transactions.insert_one(
            {
                "num_compte_source":id_compte_source,
                "type_transaction":type_transaction,
                "description_transaction":description_transaction,
                "date_transaction":datetime.datetime.now(),
                "montant":montant,
                "num_compte_destination":id_compte_destination
            }
        )
        return

    db.Transactions.insert_one(
            {
                "num_compte_source":id_compte_source,
                "type_transaction":type_transaction,
                "description_transaction":description_transaction,
                "date_transaction":datetime.datetime.now(),
                "montant":montant,
            }
        )


def get_transactions(discord_id):
    try:
        id_compte=get_compte_bancaire(discord_id)["_id"]
    except StopIteration:
        raise(ValueError("pas de compte!"))

    return db.Transactions.find({"$or":[{"num_compte_source":id_compte},{"num_compte_destination":id_compte}]})

def supprime_all_transactions(discord_id_source:str):
    ids=get_compte_bancaire(discord_id_source)
    for id in ids:
        db.Transactions.delete_many({"num_compte_source":id})

def supprime_transaction(transaction_id):
    id=ObjectId(transaction_id)
    db.Transactions.delete_one({"_id":id})

def mort_rp(discord_ID:str):
    '''
    supprime toutes les informations du joueur correspondant dans toutes les tables
    '''
    try:
        supprime_carte_grise_joueur(discord_ID)
    except Exception as e:
        print(e)
    try:
        supprime_compte_bancaire(discord_ID)
    except Exception as e:
        print(e)
    try:
        supprime_all_transactions(discord_ID)
    except Exception as e:
        print(e)
    try:
        supprime_inventaire(discord_ID)
    except Exception as e:
        print(e)
    try:
        supprime_identites(discord_ID)
    except Exception as e:
        print(e)

def cree_inventaire(discord_ID:str):
    ids=get_id(discord_ID)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.insert_one(
        {
            "id_identite":ids["_id"],
            "cash":0.0,
            "permis_conduire":False,
            "permis_port_arme":False,
            "SAC_NOMS":[],
            "SAC_QUANTITE":[]
        }
    )

def supprime_inventaire(discord_ID:str):
    ids=get_id(discord_ID)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    db.Inventaire.delete_many({"id_identite":ids["_id"]})
def get_boutique():
    '''
    renvoie un dictionnaire avec les items de la boutique et leurs prix
    '''
    return db.boutique.find({})

def get_item(nom_item:str):
    return db.boutique.find_one({"nom":nom_item})

def ajouter_objet_boutique(nom_objet:str,prix:float):
    '''
    ajoute un objet à la boutique
    '''
    db.boutique.insert_one({
        "nom":nom_objet,
        "prix":prix
    })

def modifier_objet_boutique(nom_objet:str,prix:float):
    '''
    modife un objet de la boutique
    '''
    db.boutique.update_one({"nom":nom_objet},{"$set",{"prix":prix}})

def modifier_nom_objet_boutique(nom_objet:str,nouveau_nom:str):
    '''
    modife un objet de la boutique
    '''
    db.boutique.update_one({"nom":nom_objet},{"$set",{"nom":nouveau_nom}})

def retirer_objet_boutique(nom_objet):
    '''
    reire un objet de la boutique
    '''
    db.boutique.delete_one({"nom":nom_objet})

def find_indice(liste_mots,mot):
    for i in range(len(liste_mots)):
        b=liste_mots[i]==mot
        if(b):
            return i
    return -1

def ajouter_objet_inventaire(discord_ID:str,nom_objet:str,quantite):
    '''
    ajoute un objet à l'inventaire du joueur
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        raise NameError("ne possède pas d'id")
    listes_inv=db.Inventaire.find_one({"id_identite":ids["_id"]},{"SAC_NOMS":1,"SAC_QUANTITE":1})
    liste_obj=listes_inv["SAC_NOMS"]

    liste_quantite=listes_inv["SAC_QUANTITE"]
    indice=find_indice(liste_obj,nom_objet)
    if(indice==-1):
        liste_obj.append(nom_objet)
        liste_quantite.append(quantite)
    else:
        liste_quantite[indice]+=quantite
    db.Inventaire.update_one({"id_identite":ids["_id"]},{"$set":{"SAC_NOMS":liste_obj,"SAC_QUANTITE":liste_quantite}})
def get_qtt_item(id_discord,nom):
    try:
        ids=get_id(id_discord)
        listes_inv=db.Inventaire.find_one({"id_identite":ids["_id"]},{"SAC_NOMS":1,"SAC_QUANTITE":1})
        liste_obj=listes_inv["SAC_NOMS"]
        liste_qtt=listes_inv["SAC_QUANTITE"]
        i=find_indice(liste_obj,nom)
        if(i==-1):
            return -1
        return liste_qtt[i]
    except:
        return -1

def retirer_objet_inventaire(discord_ID:str,nom_objet,quantite):
    '''
    reire un objet de l'inventaire
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return False
    listes_inv=db.Inventaire.find_one({"id_identite":ids["_id"]},{"SAC_NOMS":1,"SAC_QUANTITE":1})
    liste_obj=listes_inv["SAC_NOMS"]
    liste_quantite=listes_inv["SAC_QUANTITE"]
    indice=find_indice(liste_obj,nom_objet)
    if(indice==-1):
        return -1

    if(liste_quantite[indice]>quantite):
        nb=quantite
        liste_quantite[indice]-=quantite
    else:
        nb=liste_quantite[indice]
        liste_obj.pop(indice)
        liste_quantite.pop(indice)
    db.Inventaire.update_one({"id_identite":ids["_id"]},{"$set":{"SAC_NOMS":liste_obj,"SAC_QUANTITE":liste_quantite}})
    return nb


def retirer_objet_inventaire2(discord_ID:str,nom_objet,quantite):
    '''
    reire un objet de l'inventaire
    '''
    ids=get_id(discord_ID)
    if(ids==None):
        return False
    listes_inv=db.Inventaire.find_one({"id_identite":ids["_id"]},{"SAC_NOMS":1,"SAC_QUANTITE":1})
    liste_obj=listes_inv["SAC_NOMS"]
    liste_quantite=listes_inv["SAC_QUANTITE"]
    indice=find_indice(liste_obj,nom_objet)
    if(indice==-1):
        return False

    if(liste_quantite[indice]>quantite):
        liste_quantite[indice]-=quantite
    if(liste_quantite[indice]==quantite):
        liste_obj.pop(indice)
        liste_quantite.pop(indice)
    if(liste_quantite[indice]<quantite):
        return False
    db.Inventaire.update_one({"id_identite":ids["_id"]},{"$set":{"SAC_NOMS":liste_obj,"SAC_QUANTITE":liste_quantite}})
    return True

def get_inventaire(discord_id:str):
    '''
    renvoie le contenu de l'inventaire du joueur
    '''
    ids=get_id(discord_id)
    if(ids==None):
        return None
    return db.Inventaire.find_one({"id_identite":ids["_id"]})

def cree_drog(nom,quantite,tps_recolte,tps_traitement,image):
    '''
    crée une drogue
    '''
    if(image==None):image='null'
    return db.drog.insert_one({
        "nom":nom,
        "quantite":quantite,
        "temps_recolte":tps_recolte,
        "temps_traitement":tps_traitement,
        "image":image
    })

def modifier_drog(nom,quantite,tps_recolte,tps_traitement,image):
    '''
    modifie la drog possédant le nom
    '''
    dr=db.drog.find_one({"nom": nom})
    if(quantite==None):
        quantite=dr["quantite"]
    if(tps_recolte==None):
        tps_recolte=dr["temps_recolte"]
    if(tps_traitement==None):
        tps_traitement=dr["temps_traitement"]
    if(image==None):
        image=dr["image"]
    return db.drog.update_one({"nom":nom},
    {"$set":{
        "quantite":quantite,
        "temps_recolte":tps_recolte,
        "temps_traitement":tps_traitement,
        "image":image
    }})

def modifier_drog_vente(nom,temps_vente=None,prix_q1=None,prix_q2=None,prix_q3=None,prix_q4=None):
    return db.drog.update_one({"nom":nom},{
        "$set":{
            "temps_vente":temps_vente,
            "prix_qualite1":prix_q1,
            "prix_qualite2":prix_q2,
            "prix_qualite3":prix_q3,
            "prix_qualite4":prix_q4
        }
    })

def get_drog_infos(nom):
    '''
    renvoie les infos d'une drog
    '''
    return db.drog.find_one({"nom":nom})
def get_drogs():
    return db.drog.find({})
def supprimer_drog(nom):
    '''
    supprime une drog
    '''
    db.drog.delete_one({"nom":nom})

def creer_braq(type,montant_min,montant_max,temps_braquage):
    '''
    crée un braquage
    '''
    if(montant_max<montant_min):
        raise ValueError("le montant maximum doit etre supérieur au montant minimum")
    db.BRAQ.insert_one({
        "type":type,
        "temps":temps_braquage,
        "montant maximum":montant_max,
        "montant minimum":montant_min
    })

def get_braq(type):
    return db.BRAQ.find_one({"type":type})

def get_braquages():
    return db.BRAQ.find({})

def modifier_braq(type,montant_min,montant_max,temps_braquage):
    '''
    modifie un braquage
    '''
    if(montant_max<montant_min):
        raise ValueError("le montant maximum doit etre supérieur au montant minimum")
    db.BRAQ.update_one({
        "type":type,
    },{"$set":{        
        "temps":temps_braquage,
        "montant maximum":montant_max,
        "montant minimum":montant_min
        }
    })
def close():
    client.close()