# Driver library to connect and use a PostrgreSQL database
import psycopg2
# Allows you to retrieve the connection parameters from the config file.ini
import configparser
# This library allows us to have information about the execution time of our code
import time
import PixelsAnalysis as pa


def read_database():
    """This function aims to save in a list all the links of the images of the buildings,
       type of roof and their ID
    """

    # To measure program execution time
    timer_start = time.time()
    buildings = []

    try:
        # Creating the connection to Postgre Database
        connexion = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (HOST, DATABASE, USER, PASSWORD))
        # Creating the SQL Query Object
        cursor = connexion.cursor()
        # We retrieve 400 verified buildings to create our dataset
        query = "SELECT id,materiau_result,lien_api FROM batiments WHERE materiau_correct='TRUE' ORDER BY id ASC LIMIT 600;"
        # Executing the query
        cursor.execute(query)

        # Iterating through the query results
        for row in cursor.fetchall():
            # We add to our list 'buildings' the tuple (ID, materiau_result, lien_api)
            buildings.append((row[0], row[1], row[2]))

    except (Exception, psycopg2.Error) as error:
        print("An error occurred while connecting to the Postgre database", error)

    finally:
        # closing database connection.
        if connexion:
            cursor.close()
            connexion.close()
            print("PostgreSQL connection closed")
            execution_time = round(time.time() - timer_start, 4)
            print(f'"batiments" table reading time :  {execution_time} ')
    return buildings


def main(choix_repartition=0):
    """
    :param choix_repartition: Si la valeur est 0 (par defaut), on decoupe les donnes en 50/50
                            si valeur est 1 : learning_dataset sera normalisé selon le type de materiau
                            le moins present
    :return:
    """
    # On split les datas selon le materiau de chaque toit
    datas = pa.split(buildings, choix_repartition)
    # creation echantillon apprentissage et echantillon de test
    learning_dataset = datas[0]
    test_dataset = datas[1]


    # Training :
    moyennes = [pa.average_pixels(avg) for avg in learning_dataset]

    #Validation :
    pa.score(test_dataset,moyennes)

if __name__ == "__main__":
    # Read config.ini file
    config_obj = configparser.ConfigParser()
    try:
        config_obj.read("ressources/configfile.ini")

        dbparam = config_obj["postgresql"]
        # Postgre PARAMETERS :
        DATABASE = dbparam["database"]
        HOST = dbparam["host"]
        USER = dbparam["user"]
        PASSWORD = dbparam["password"]

        buildings = read_database()
        print("NB : ", len(buildings))


    except OSError as err:
        print("OS error: {0}".format(err))
        print("Unable to find file 'configfile.ini' !")

    main(1)
