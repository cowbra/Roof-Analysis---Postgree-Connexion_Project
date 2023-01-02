# Ancienne version, (il ne faut pas devoiler tout ses atoux pour gagner la competition)

import configparser
import time
from datetime import timedelta
from io import BytesIO

import requests
from PIL.Image import *
from numpy import argmin
import random
import copy


def split(batiments, choix_repartition):
    toit_tuiles = []
    toit_beton = []
    toit_ardoises = []
    toit_zincAluminium = []

    # On ajoute tous les batiements autres que 'indetermine' dans leur categorie
    for building in batiments:
        if building[1] == "Beton":
            toit_beton.append((building))
        elif building[1] == "Tuiles":
            toit_tuiles.append(building)
        elif building[1] == "Ardoises":
            toit_ardoises.append(building)
        elif building[1] == "Zinc Aluminium":
            toit_zincAluminium.append(building)

    random.shuffle(toit_beton)
    random.shuffle(toit_tuiles)
    random.shuffle(toit_ardoises)
    random.shuffle(toit_zincAluminium)

    learning_set = [toit_beton[:len(toit_beton) // 2], toit_tuiles[:len(toit_tuiles) // 2],
                    toit_ardoises[:len(toit_ardoises) // 2], toit_zincAluminium[:len(toit_zincAluminium) // 2]]

    if choix_repartition == 1:
        # normalisation des listes sur le materiau le moins present
        taille = [len(i) for i in learning_set]
        mini = min(taille)
        learn2 = []

        for liste in learning_set:
            learn2.append(liste[:mini])
        learning_set = learn2


    test_set = [toit_beton[len(toit_beton) // 2:] + toit_tuiles[len(toit_tuiles) // 2:] +
                toit_ardoises[len(toit_ardoises) // 2:] + toit_zincAluminium[len(toit_zincAluminium) // 2:]]

    print("taille beton :", len(learning_set[0]))
    return learning_set, test_set


def average_pixels(toits):
    rouges = []
    verts = []
    bleus = []
    i = 0
    taille = len(toits)
    start = time.time()
    for elt in toits:
        i += 1
        if i % 200 == 0:
            print("\nlecture image en cours :", i, "/", taille)
            delta_t = round(time.time() - start)
            print("temps pour 200 images :", delta_t, "sec")
            time_left = delta_t * (taille - i)
            td = timedelta(seconds=time_left)
            a = time.strftime('%H:%M:%S', time.gmtime(time_left))
            print('Temps restant estimé :', a)
            start = time.time()
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

# Test_image = "https://wxs.ign.fr/ortho/geoportail/r/wms?SERVICE=WMS&VERSION=1.3.0&LAYERS=HR.ORTHOIMAGERY.ORTHOPHOTOS&EXCEPTIONS=text/xml&FORMAT=image/jpeg&SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap&STYLES=&CRS=EPSG:4326&BBOX=43.68581529756786,4.129607156785642,43.686043447002405,4.129912678428446&WIDTH=256&HEIGHT=256"
# print(Type_de_toit_predit(Test_image))
