
# This library allows us to have information about the execution time of our code
import time
import PixelsAnalysis as pa
import seaborn as sns
import matplotlib.pyplot as plt
import csv

def read_file():
    buildings=[]
    with open("./ressources/images/batiments.csv", 'r') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            buildings.append(row)
    return buildings

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
        query = "SELECT id,materiau_result,lien_api FROM batiments WHERE materiau_correct='TRUE' ORDER BY id ASC LIMIT 800;"
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
    score =pa.score(test_dataset,moyennes)
    sns.heatmap(score[1], square=True, annot=True)
    plt.show()
    return score


read_file()
check = False
if __name__ == "__main__" and check:


    large_tests = False
    if large_tests:
        accuracy_with_normalization = 0
        accuracy_without_normalization = 0
        confusion_matrix_with_normalization = [[0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0]]
        confusion_matrix_without_normalization = [[0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0]]

        NB_RUN = 2

        for i in range(NB_RUN):
            start=time.time()
            print("step ",i,"/",NB_RUN)
            result_normalized = main(1)
            result = main(0)

            accuracy_with_normalization += result_normalized[0]
            accuracy_without_normalization += result[0]
            for x in range(4):
                for y in range(4):
                    confusion_matrix_without_normalization[x][y] +=result[1][x][y]
                    confusion_matrix_with_normalization[x][y] += result_normalized[1][x][y]

            print("step ",i, "finished in ",round(time.time()-start,2),"sec.")
        accuracy_with_normalization = round(accuracy_with_normalization/NB_RUN,2)
        accuracy_without_normalization = round(accuracy_without_normalization / NB_RUN,2)
        for x in range(4):
            for y in range(4):
                confusion_matrix_without_normalization[x][y] = round(confusion_matrix_without_normalization[x][y]/NB_RUN,2)
                confusion_matrix_with_normalization[x][y] = round(confusion_matrix_with_normalization[x][y]/NB_RUN,2)

        print("Accuracy with normalization on ",NB_RUN," run : ",accuracy_with_normalization,"%")
        print("Accuracy without normalization on ",NB_RUN," run : ", accuracy_without_normalization,"%")

        sns.heatmap(confusion_matrix_without_normalization, square=True, annot=True)
        plt.show()
        sns.heatmap(confusion_matrix_with_normalization, square=True, annot=True)
        plt.show()

    else:
        main(1)

