import sqlite3
from os import getcwd

class MessageHistory:
    def __init__(self, database_name, current_conversation):
        self.__database_name = database_name
        self.__current_conversation = current_conversation
        self.__is_initialized = False
        self.initialize()

    def __get_database_name(self):    
        return self.__database_name
    
    def __get_current_conversation(self):
        return self.__current_conversation
    
    def __set_current_conversation(self, value: str | int):
        self.__current_conversation = str(value)
    
    def __get_is_initialized(self):
        return self.__is_initialized
    
    def __set_is_initialized(self, value: bool):
        self.__is_initialized = value
    
    database_name = property(fget=__get_database_name)
    current_conversation = property(fget=__get_current_conversation, fset=__set_current_conversation)
    is_initialized = property(fget=__get_is_initialized, fset=__set_is_initialized)

    def open_connection(self):
        connection = sqlite3.connect(getcwd() + f"\\{self.database_name}")
        cursor = connection.cursor()
        return (connection, cursor)

    def close_connection(self, connection):
        connection.close()



    def create_conversation_tracker_table(self, cursor):
        cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_tracker(
            id INTEGER PRIMARY KEY,
            conversation INTEGER NOT NULL
        )
        """
        )

    def initialize_database(self):
        (connection, cursor) = self.open_connection()
        self.create_conversation_tracker_table(cursor=cursor)
        self.close_connection(connection=connection)

    def is_database_empty(self) -> bool:
        (connection, cursor) = self.open_connection()

        result = (cursor.execute(
        """
        SELECT conversation FROM conversation_tracker
        """
        )).fetchall()

        self.close_connection(connection=connection)

        if len(result) == 0:
            return True
        
        return False

    def initialize(self):
        self.initialize_database()

        if self.is_database_empty():
            self.create_new_conversation()
        
        self.is_initialized = True



    def insert_message(self, message: dict[str,str], attachment: str | None): #TODO: message is a dictionary or a list of dictionaries for finetuning
        (connection, cursor) = self.open_connection()
        
        if attachment == None:
            cursor.executemany(
            """
            INSERT INTO _{}(message,sender,has_attachment)
            VALUES (?,?,?)
            """.format(self.current_conversation), 
            [(message["message"],message["sender"],0)]
            )
        elif type(attachment) == 'str': #there's an image attached to the message
            cursor.executemany(
            """
            INSERT INTO _{}(message,sender,has_attachment,attachment)
            VALUES (?,?,?,?)
            """.format(self.current_conversation), 
            [(message["message"],message["sender"],1,attachment)]
            )
        connection.commit()

        self.close_connection(connection=connection)

    def get_messages(self) -> list[dict[str,str]]:
        (connection, cursor) = self.open_connection()

        results = (cursor.execute(
        """
        SELECT message,sender FROM _{}
        """.format(self.current_conversation)
        )).fetchall()

        self.close_connection(connection=connection)

        messages = []

        for message in results:
            messages.append(
                {
                    "message": f"{message[0]}", 
                    "sender": f"{message[1]}"
                }
            ) 

        return messages




    def get_next_conversation_name(self, cursor):
        #Uses numbers for names

        list_of_rows_in_table = (cursor.execute(
        """
        SELECT conversation FROM conversation_tracker ORDER BY conversation DESC
        """
        )).fetchall()

        if len(list_of_rows_in_table) == 0:
            return 1

        #A list that contains tuples, which contain the value from the table as the first value
        newest_conversation = list_of_rows_in_table[0][0]

        next_conversation = newest_conversation + 1

        return next_conversation

    def update_conversation_tracker(self, connection, cursor, next_conversation):
        cursor.executemany(
        """
        INSERT INTO conversation_tracker(conversation)
        VALUES (?)
        """, [(next_conversation,)]
        )
        connection.commit()

    def create_new_conversation(self):
        (connection, cursor) = self.open_connection()
        
        next_conversation = self.get_next_conversation_name(cursor=cursor)

        cursor.execute( #has_attachment 1 = yes, 0 = no
        """
        CREATE TABLE _{}(
            id INTEGER PRIMARY KEY,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            has_attachment INTEGER NOT NULL,
            attachment TEXT
        )
        """.format(next_conversation)
        )

        self.update_conversation_tracker(
            connection=connection,
            cursor=cursor,
            next_conversation=next_conversation
        )

        self.close_connection(connection=connection)

    def change_current_conversation(self, conversation_name):
        self.current_conversation = conversation_name



    def info(self):
        current_conversation = self.current_conversation
        is_initialized = self.is_initialized
        database_name = self.database_name
        
        (connection, cursor) = self.open_connection()

        tables_in_database = (cursor.execute(
        """
        SELECT conversation FROM conversation_tracker
        """
        )).fetchall()

        self.close_connection(connection=connection)
        
        print("\n")
        print("-----")
        print("Is the message history initialized: ", is_initialized)
        print("The name of the database: ", database_name)
        print("The tables in the database", tables_in_database)
        print("The current conversation: ", current_conversation)
        print("-----")
        print("\n")

        