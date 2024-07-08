import mysql.connector 
from mysql.connector import Error

def connect_db():

    db_name = 'Workout'
    user = "root"
    password = 'Nano8312!'
    host = 'localhost'      

    try:
        conn = mysql.connector.connect(
            database = db_name,
            user = user,
            password = password,
            host = host
        )

        if conn.is_connected():
            print("Successfully connected to the database!")
            return conn 

    except Error as e:
        print(f'Error: {e}')
        return None