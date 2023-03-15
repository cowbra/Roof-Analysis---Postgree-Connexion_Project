import psycopg2
import csv
import configparser
from psycopg2 import extras
from psycopg2.extras import execute_batch


#Read config.ini file
config_obj = configparser.ConfigParser()
try :
    config_obj.read("./ressources/configfile.ini")

except OSError as err:
    print("OS error: {0}".format(err))
    print("Vous n'avez pas ajouté le fichier 'configfile.ini' !")
dbparam = config_obj["postgresql"]

# Postgre PARAMETERS :
DATABASE = dbparam["database"]
HOST = dbparam["host"]
USER = dbparam["user"]
PASSWORD= dbparam["password"]

# Connect to the database
conn = psycopg2.connect(
    dbname=DATABASE,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port="5432"
)

with open('./ressources/batiments_all.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', fieldnames=['id', 'lien_api_infra'])
    i = 0  # counter for number of updates
    for row in reader:
        # Update the 'lien_api_infra' column for the corresponding 'id'
        cur = conn.cursor()
        cur.execute(
            "UPDATE public.batiments SET lien_api_infra = %s WHERE id = %s",
            (row['lien_api_infra'], row['id'])
        )
        cur.close()
        i += 1
        if i % 50000 == 0:
            conn.commit()
            print(f"Committed {i} updates")
    # Commit any remaining updates
    conn.commit()
    print(f"Committed {i} updates")

# Close the database connection
conn.close()
