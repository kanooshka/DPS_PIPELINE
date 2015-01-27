import mysql.connector

cnx = mysql.connector.connect(user='root', password='poop',host='127.0.0.1',database='dpstudio')
cursor = cnx.cursor()

query = ("SELECT startframe FROM shots")
               
cursor.execute(query)
                              
for (index) in cursor:
  print(index)

cursor.close()
cnx.close()