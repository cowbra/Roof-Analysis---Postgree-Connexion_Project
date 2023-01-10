
import time
from datetime import timedelta
from io import BytesIO

import requests
from PIL.Image import *
from numpy import argmin
import random
import seaborn as sns



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


    test_set = toit_beton[len(toit_beton) // 2:] + toit_tuiles[len(toit_tuiles) // 2:] + toit_ardoises[len(toit_ardoises) // 2:] + toit_zincAluminium[len(toit_zincAluminium) // 2:]
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
        response = requests.get(elt[2])


        image = open(BytesIO(response.content))
        (rouge, vert, bleu) = (0,0,0)
        #On fait la moyenne pour chaque pixel du bloc central de 16x16
        for x in range(16):
            for y in range(16):
                (rouge, vert, bleu) = (x + y for x, y in zip((rouge, vert, bleu), image.getpixel((120+x, 120+y))))
        image.close()

        rouges.append(round(rouge/16,5))
        verts.append(round(vert/16,5))
        bleus.append(round(bleu/16,5))

    print("lecture des images terminee pour le materiau (4 en tout)")
    moy_rouge = sum(rouges) / len(rouges)
    moy_vert = sum(verts) / len(verts)
    moy_bleu = sum(bleus) / len(bleus)
    result = [moy_rouge, moy_vert, moy_bleu]
    return result


def Type_de_toit_predit(image_a_predire,avg):
    response = requests.get(image_a_predire)

    avg_pixels_tuiles = avg[0]
    avg_pixels_ardoises = avg[1]
    avg_pixels_beton = avg[2]
    avg_pixels_zincAlu = avg[3]

    image = open(BytesIO(response.content))

    [rouge, vert, bleu] = [0, 0, 0]
    # On fait la moyenne pour chaque pixel du bloc central de 16x16
    for x in range(16):
        for y in range(16):
            [rouge, vert, bleu] = (x + y for x, y in zip((rouge, vert, bleu), image.getpixel((120 + x, 120 + y))))
    image.close()

    [rouge, vert, bleu] = [round(rouge/16,5), round(vert/16,5), round(bleu/16,5)]


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

    result_indice = [sum(Is_Beton), sum(Is_tuiles), sum(Is_Ardoises), sum(Is_Zinc)]
    result_name = ["Beton", "Tuiles", "Ardoises", "Zinc Aluminium"]

    return result_name[argmin(result_indice)]


def score(test_dataset,avg):
    classes = ["Beton","Tuiles", "Ardoises", "Zinc Aluminium"]
    im_prediction = [0,0,0,0]
    im_true = [0,0,0,0]
    conf_matrix = [[0,0,0,0],
                  [0,0,0,0],
                  [0,0,0,0],
                  [0,0,0,0]]
    print("Validation en cours")
    for image in test_dataset:
        # Image test = (ID,type,lien)
        identified_as = Type_de_toit_prediIDt(image[2],avg)
        # On modifie la matrice de confusion en fonction du resultat
        # On classe de cette maniere : beton,tuiles,ardoises,zinc
        x,y = classes.index(image[1]),classes.index(identified_as)
        conf_matrix[x][y] += 1

    print(conf_matrix)
    #sns.heatmap(conf_matrix, square=True, annot=True, fmt='d')
    #plt.show()
    return round((conf_matrix[0][0] + conf_matrix[1][1] + conf_matrix[2][2] + conf_matrix[3][3]) / len(test_dataset) * 100 , 4), conf_matrix
