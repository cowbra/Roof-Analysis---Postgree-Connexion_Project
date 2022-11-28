# Roof Analysis & Postgre Connexion_Project
 
## 🌟 Goal

> Send data of buildings to database, analyze their structure,...

## 👷 Prerequisites

1. install the python libraries below
2. Retrieve the configuration file 'configfile.ini' to connect to the database (caution: check that the file is in the .gitignore)

## 🗒 How it works

1. Install python libraries with `pip`
   > ```shell
   >  pip install -r ressources/requirements.txt
   > ```
2. If you need to send data to the database, check that the `buildingList.json` file is up-to-date
   > This file should be placed in the resources folder and can be found on Teams:
   > ```
   > General > DATASET > buildingList.json
   > ```
3. Put the database credentials (contained in the 'configfile.ini) in the `ressources` folder
   > This file should be placed in the resources folder and can be found on Teams:
   > ```
   > General > DATASET > Base De Données - PI² > configfile.ini
   > ```

4. How to run the program?
   > ```
   > One file for each use.
   > Launch the one you need
   > ```

## 🔨 DATASET CREATION - How to retrieve verified buildings from the database ? 📑

1. Importing the necessary modules
   ``` python
   # Driver library to connect and use a PostrgreSQL database
   import psycopg2 
   # Allows you to retrieve the connection parameters from the config file.ini
   import configparser
   # This library allows us to have information about the execution time of our code
   import time
    ```
2. We now need to retrieve the credentials to connect to the Postgre database
   > These can be found in the `configfile.ini` file
   > Here is how to read this configuration file in python :   
   ``` python
    # Read config.ini file
    config_obj = configparser.ConfigParser()
    try:
        config_obj.read("configfile.ini")
   
    except OSError as err:
        print("OS error: {0}".format(err))
        print("Unable to find file 'configfile.ini' !")
    dbparam = config_obj["postgresql"]

    # Postgre PARAMETERS :
    DATABASE = dbparam["database"]
    HOST = dbparam["host"]
    USER = dbparam["user"]
    PASSWORD = dbparam["password"]
    ```
3. Now that we have the prerequisites to retrieve our information, let's create the function that allows us to do this
    ``` python
    def read_database():
    """This function aims to save in a list all the links of the images of the buildings,
     type of roof and their ID"""

    # To measure program execution time
    timer_start = time.time()
    buildings = []
   
    try:
        # Creating the connection to Postgre Database
        connexion = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (HOST, DATABASE, USER, PASSWORD))
        # Creating the SQL Query Object
        cursor = connexion.cursor()
        # We retrieve 400 verified buildings to create our dataset
        query = "SELECT id,materiau_result,lien_api FROM batiments WHERE materiau_correct='TRUE' LIMIT 400;"
        # Executing the query
        cursor.execute(query)

        # Iterating through the query results
        for row in cursor.fetchall():
            # We add to our list 'buildings' the tuple (ID, materiau_result, lien_api)
            buildings.append((row[0], row[1],row[2]))

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
    ```
## Now that you have unlocked 🔓 your skills, it's up to you 👊!