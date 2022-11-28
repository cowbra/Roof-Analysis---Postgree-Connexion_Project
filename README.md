# Roof Analysis & Postgree Connexion_Project
 
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
2. If you need to send data to the database, check that the `buildingList.json` file is up to date
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
   > One file for each use
   > Launch the one you need
