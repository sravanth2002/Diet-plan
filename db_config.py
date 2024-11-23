import mysql.connector
def connect_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0401",
            database="foodplangen"
        )
        print("Database connection successful")
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
