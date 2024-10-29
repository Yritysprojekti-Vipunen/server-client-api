import mysql.connector
from mysql.connector import Error
import io

# Create connection to the MySQL database
user = "root" #Oma käyttäjätunnus
password = "Yritysprojekti2" #Oma salasana


def create_connection():
    try:
        #MUOKKAA OMAT TIEDOT TÄHÄN!
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user=user,
            password=password,
            database="chatbot_message_history"
        )
        return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

# Tallennetaan viestihistoria
def save_message(user_id, message, sender):
    connection = create_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        sql = "INSERT INTO conversation_history (user_id, message, sender) VALUES (%s, %s, %s)"
        values = (user_id, message, sender)
        cursor.execute(sql, values)
        connection.commit()
        print("Message saved successfully")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Haetaan viestihistoria tietyltä ajanjaksolta
def get_convertations() -> list:
    connection = create_connection()
    if connection is None:
        return
    try:
        cursor = connection.cursor()
        sql = "SELECT message, sender FROM conversation_history WHERE DATE(timestamp) = CURDATE();"
        cursor.execute(sql)
       
        results = cursor.fetchall()

        messages = []
        for row in results:
            messages.append(
                {
                    "role": f"{row[1]}",
                    "content": f"{row[0]}"
                }
            )

        return messages

    except Error as e:
        print(f"Error: '{e}'")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def insert_file_into_database(file_path):
    connection = create_connection()
    cursor = connection.cursor()

    try:
        with open(file_path, 'rb') as file:
            pdf_data = file.read()
        
        cursor.execute(
        '''
        INSERT INTO file_storage (file_name, file_data) 
        VALUES (%s, %s)
        ''', (file_path.split('/')[-1], pdf_data)
        )
        
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_file_from_database(file_id: int):
    connection = create_connection()
    cursor = connection.cursor()

    file_contents = None

    try:
        cursor.execute(
        '''
        SELECT file_data FROM file_storage WHERE id = %s
        ''', (file_id,)
        )
        
        row = cursor.fetchone()

        stream = io.BytesIO() #in-memory storage for the file

        if row:
            stream.write(row[0])
            stream.seek(0)
            file_contents = stream.read()
            stream.close()
        else:
            print("No file found with the specified ID.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

        return file_contents
