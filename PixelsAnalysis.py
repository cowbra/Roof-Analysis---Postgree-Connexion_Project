import psycopg2
import configparser
import time
from datetime import timedelta
from PIL.Image import *
from numpy import argmin
import requests
from io import BytesIO


def read_database():
    """Cette fonction a pour but de sauvegarder dans une liste tous les liens des
     images des batiments ainsi que leur type de toit"""

    start = time.time()
    result = []
    try:
        # On cree la connexion a la bdd Postgre
        connexion = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (HOST, DATABASE, USER, PASSWORD))
        cursor = connexion.cursor()
        query = "SELECT materiau_result,lien_api FROM batiments"
        cursor.execute(query)

        # on parcourt les resultats de la requete
        for row in cursor.fetchall():
            # on ajoute dans la liste result des tuples (materiau_result,lien_api)
            result.append((row[0], row[1]))


    except (Exception, psycopg2.Error) as error:
        print("Une erreur est survenue pendant la connexion avec la bdd Postgre", error)

    finally:
        # closing database connection.
        if connexion:
            cursor.close()
            connexion.close()
            print("PostgreSQL connexion fermee")
            temps = round(time.time() - start, 4)
            print(f'Temps de lecture de la table "batiments" :  {temps} ')
    return result


def analysis_pixels(batiments):
    toit_tuiles = []
    toit_beton = []
    toit_ardoises = []
    toit_zincAluminium = []

    # On ajoute tous les batiements autres que 'indetermine' dans leur categorie
    for building in batiments:
        if building[0] == "Beton":
            toit_beton.append((building))
        elif building[0] == "Tuiles":
            toit_tuiles.append(building)
        elif building[0] == "Ardoises":
            toit_ardoises.append(building)
        elif building[0] == "Zinc Aluminium":
            toit_zincAluminium.append(building)

    # Listes contenant la moyenne des pixels de chaque type de toit et un ecart relatif sur ce dernier
    print("debug 2\n")
    return average_pixels(toit_tuiles), average_pixels(toit_ardoises), average_pixels(toit_beton), average_pixels(
        toit_zincAluminium)


def average_pixels(toits):
    rouges = []
    verts = []
    bleus = []
    i=0
    taille=len(toits)
    start=time.time()
    for elt in toits:
        i+=1
        if i %200 ==0:
            print("\nlecture image en cours :",i,"/",taille)
            delta_t = round(time.time()-start)
            print("temps pour 200 images :",delta_t,"sec")
            time_left = delta_t*(taille-i)
            td = timedelta(seconds=time_left)
            a = time.strftime('%H:%M:%S', time.gmtime(time_left))
            print('Temps restant estimé :', a)
            start=time.time()
        response = requests.get(elt[1])

        image = open(BytesIO(response.content))
        (rouge, vert, bleu) = image.getpixel((128, 128))
        image.close()

        rouges.append(rouge)
        verts.append(vert)
        bleus.append(bleu)
    print("lecture des images terminee")
    moy_rouge = sum(rouges) / len(rouges)
    moy_vert = sum(verts) / len(verts)
    moy_bleu = sum(bleus) / len(bleus)
    result = [moy_rouge, moy_vert, moy_bleu]

    return result


def Type_de_toit_predit(image_a_predire):
    response = requests.get(image_a_predire)


    avg = analysis_pixels(read_database())

    avg_pixels_tuiles = avg[0]
    avg_pixels_ardoises = avg[1]
    avg_pixels_beton = avg[2]
    avg_pixels_zincAlu = avg[3]

    image = open(BytesIO(response.content))
    [rouge, vert, bleu] = image.getpixel((128, 128))
    image.close()
    Is_tuiles = [abs(rouge - avg_pixels_tuiles[0]),
                 abs(vert - avg_pixels_tuiles[1]),
                 abs(bleu - avg_pixels_tuiles[2])]

    Is_Ardoises = [abs(rouge - avg_pixels_ardoises[0]),
                   abs(vert - avg_pixels_ardoises[1]),
                   abs(bleu - avg_pixels_ardoises[2])]

    Is_Beton = [abs(rouge - avg_pixels_beton[0]),
                abs(vert - avg_pixels_beton[1]),
                abs(bleu - avg_pixels_beton[2])]

    Is_Zinc = [abs(rouge - avg_pixels_zincAlu[0]),
               abs(vert - avg_pixels_zincAlu[1]),
               abs(bleu - avg_pixels_zincAlu[2])]

    result_indice = [sum(Is_tuiles), sum(Is_Ardoises), sum(Is_Beton), sum(Is_Zinc)]
    result_name = ["Tuiles", "Ardoises", "Beton", "Zinc Aluminium"]
    return result_name[argmin(result_indice)]


if __name__ == "__main__":
    # Read config.ini file
    config_obj = configparser.ConfigParser()
    try:
        config_obj.read("configfile.ini")

    except OSError as err:
        print("OS error: {0}".format(err))
        print("Vous n'avez pas ajouté le fichier 'configfile.ini' !")
    dbparam = config_obj["postgresql"]

    # Postgre PARAMETERS :
    DATABASE = dbparam["database"]
    HOST = dbparam["host"]
    USER = dbparam["user"]
    PASSWORD = dbparam["password"]

    Test_image = "https://wxs.ign.fr/ortho/geoportail/r/wms?SERVICE=WMS&VERSION=1.3.0&LAYERS=HR.ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&STYLES=&CRS=EPSG:4326&BBOX=43.68581529756786,4.129607156785642,43.686043447002405,4.129912678428446&WIDTH=256&HEIGHT=256"
    print(Type_de_toit_predit(Test_image))
