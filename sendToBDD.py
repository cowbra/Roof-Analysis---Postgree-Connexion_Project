# importation de la librairie permettant la connexion a la db postgre
import psycopg2
import json
import configparser

def read_json(file_path):
    values = []

    with open(file_path) as json_data:
        data = json.load(json_data)
    data = json.loads(json.dumps(data))
    print(len(data))

    for k,v in data.items():
        id = v['id']
        rightTop_x = v['right_top_x']
        rightTop_y = v['left-bottom_y']
        leftBottomm_x = v['left-bottom_x']
        leftBottomm_y = v['left-bottom_y']
        lienApi = v['lien_api']
        materiau = v['materiau_result']
        values.append((id,rightTop_x,rightTop_y,leftBottomm_x,leftBottomm_y,lienApi,materiau))

    return values

def send_to_database(values):
    # Opening connection
    conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (HOST, DATABASE, USER, PASSWORD))
    conn.autocommit = True

    # creating a cursor
    cursor = conn.cursor()

    sous_liste = []
    for i in range(len(values)):
        sous_liste.append(values[i])

        #on envoie les batiments par 10 000 pour éviter une surcharge
        if i%10000 == 0 :
            # executing sql statement
            cursor.executemany("INSERT INTO batiments VALUES(%s,%s,%s,%s,%s,%s,%s)", sous_liste)
            print(i,"/",len(values)," batiments envoyés")
            sous_liste=[]

    # on execute les valeurs restantes
    cursor.executemany("INSERT INTO batiments VALUES(%s,%s,%s,%s,%s,%s,%s)", sous_liste)
    # committing changes
    conn.commit()

    # closing connection
    conn.close()
    print("Upload Completed")


#Read config.ini file
config_obj = configparser.ConfigParser()
try :
    config_obj.read("configfile.ini")

except OSError as err:
    print("OS error: {0}".format(err))
    print("Vous n'avez pas ajouté le fichier 'configfile.ini' !")
dbparam = config_obj["postgresql"]

# Postgre PARAMETERS :
DATABASE = dbparam["database"]
HOST = dbparam["host"]
USER = dbparam["user"]
PASSWORD= dbparam["password"]

# Our generated data
file = "ressources/buildingList.json"



send_to_database(read_json(file))




