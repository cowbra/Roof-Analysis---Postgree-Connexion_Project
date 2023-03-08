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

# Open the CSV file and iterate over each row
with open('./ressources/batiments_all.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=';', fieldnames=['id', 'lien_api_infra'])
    updates = []
    for row in reader:
        # Append the tuple with new value and id to the updates list
        updates.append((row['lien_api_infra'], row['id']))
        if len(updates) == 50000:
            # Execute the batch update query
            execute_batch(cur, "UPDATE public.batiments SET lien_api_infra = %s WHERE id = %s", updates)
            conn.commit()
            print(f"Committed {len(updates)} updates")
            # Clear the updates list
            updates = []
    # Execute any remaining updates
    execute_batch(cur, "UPDATE public.batiments SET lien_api_infra = %s WHERE id = %s", updates)
    conn.commit()
    print(f"Committed {len(updates)} updates")

# Close the database connection
conn.close()
