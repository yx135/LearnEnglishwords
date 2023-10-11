import toml
import streamlit as st
import mysql.connector
import os
import logging
from mysql.connector import Error
logging.basicConfig(level=logging.INFO,

                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

path=os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = "words"
# Load credentials from secrets.toml
#secrets = toml.load("secrets.toml")
#mysql_config = secrets["connections"]["mysql"]



def create_connection():
    """Create a database connection and return the connection object."""
    connection = None
    logging.info(f"连接mysql数据库")
    logging.info(f"host: {st.secrets.host}")
    logging.info(f"user: {st.secrets.user}")
    logging.info(f"password: {st.secrets.password}")
    logging.info(f"database: {st.secrets.database}")
    logging.info(f"port: {st.secrets.port}")
    try:
        connection = mysql.connector.connect(
            host=st.secrets.host,
            user=st.secrets.user,
            password=st.secrets.password,
            database=st.secrets.database,
            port=st.secrets.port
           
            #host="zeabur-gcp-asia-east1-1.clusters.zeabur.com",
            #user="root",
            #password="s13KZ86Uk05J",
            #database="words",
            #port="31673"
            
        )
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"The error '{e}' occurred")
        return None
def setup_database():
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            # Create tables if they don't exist
            # Added frequency column
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS word (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    word TEXT ,
                    language TEXT,
                    example_sentence TEXT,
                    chinese_translation TEXT,
                    frequency INTEGER DEFAULT 0,
                    UNIQUE(word(100))              
                )
            """)

            # Added frequency column
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS root_or_affix (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    text TEXT ,
                    type TEXT,
                    chinese_translation TEXT,
                    frequency INTEGER DEFAULT 0,
                    UNIQUE(text(100))
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS word_to_ra (
                    word_id INTEGER,
                    ra_id INTEGER,
                    FOREIGN KEY(word_id) REFERENCES word(id),
                    FOREIGN KEY(ra_id) REFERENCES root_or_affix(id),
                    UNIQUE(word_id, ra_id)
                )
            """)
            connection.commit()
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
def word_exit(word):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM word WHERE word=%s", (word,))
            word_id = cursor.fetchone()
            return word_id
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
def update_word(word):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE word SET frequency = frequency + 1 WHERE word=%s", (word,))
            connection.commit()
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()

def insert_word(word, language, example_sentence, chinese_translation):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT  INTO word (word, language, example_sentence, chinese_translation)
                VALUES (%s, %s, %s, %s)
            """, (word, language, example_sentence, chinese_translation))
            # If word already exists, update its frequency
            cursor.execute("""
                UPDATE word 
                SET frequency = frequency + 1 
                WHERE word = %s
            """, (word,))
            connection.commit()
            cursor.execute("SELECT id FROM word WHERE word=%s", (word,))
            word_id = cursor.fetchone()[0]
            return word_id
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()    

def insert_root_or_affix(text, ra_type, chinese_translation):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT  INTO root_or_affix (text, type, chinese_translation)
                VALUES (%s, %s, %s)
            """, (text, ra_type, chinese_translation))
            # If root or affix already exists, update its frequency
            cursor.execute("""
                UPDATE root_or_affix 
                SET frequency = frequency + 1 
                WHERE text = %s
            """, (text,))
            connection.commit()
            cursor.execute("SELECT id FROM root_or_affix WHERE text=%s", (text,))
            ra_id = cursor.fetchone()[0]
            return ra_id
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
   
def link_word_to_ra(word_id, ra_id):
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO word_to_ra (word_id, ra_id)
                VALUES (%s, %s)
            """, (word_id, ra_id))
            connection.commit()
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()


def get_word_details(word):
    connection = create_connection()
    if connection is None:  # Check if connection was successful
        print("Failed to connect to the database")
        return []
    try:
        with connection.cursor(buffered=True) as cursor:
            details = {"word": word, "roots": [], "prefixes": [], "suffixes": []}
            cursor.execute("SELECT chinese_translation, example_sentence,frequency FROM word WHERE word=%s", (word,))
            result = cursor.fetchone()
            details["chinese_translation"] = result[0]
            details["example_sentence"] = result[1]
            details["frequency"]=result[2]

            cursor.execute("""
                SELECT r.text, r.type, r.chinese_translation 
                FROM word_to_ra wtr
                JOIN root_or_affix r ON wtr.ra_id = r.id
                WHERE wtr.word_id = (SELECT id FROM word WHERE word = %s)
            """, (word,))

            for row in cursor.fetchall():
                text, ra_type, translation = row
                if ra_type == "root":
                    details["roots"].append({"text": text, "chinese_translation": translation})
                elif ra_type == "prefix":
                    details["prefixes"].append({"text": text, "chinese_translation": translation})
                elif ra_type == "suffix":
                    details["suffixes"].append({"text": text, "chinese_translation": translation})
            connection.close()
            return details
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
def get_all_words():
    """
    Fetches all the words from the word table in the database.
    
    Returns:
        List of dictionaries, each dictionary contains word details.
    """
    connection = create_connection()
    try:
        with connection.cursor(buffered=True) as cursor:
            cursor.execute("SELECT word, language, example_sentence, chinese_translation,frequency FROM word")
            rows = cursor.fetchall()
            # Convert the fetched rows into a list of dictionaries for easy use
            words = []
            for row in rows:
                word_detail = {
                    "word": row[0],
                    "language": row[1],
                    "example_sentence": row[2],
                    "chinese_translation": row[3],
                    "frequency":row[4]
                }
                words.append(word_detail)
            return words
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
    

def get_root_or_affix_details(text=None):
    """
    Fetch details from the root_or_affix table.
    
    Args:
    - text (str, optional): The text to filter by. Defaults to None, meaning it will return all records.
    
    Returns:
    - List of dictionaries containing details from the root_or_affix table.
    """
    connection = create_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, text, type, chinese_translation FROM root_or_affix")
            rows = cursor.fetchall()
            # Convert the fetched rows into a list of dictionaries
            details = []
            for row in rows:
                detail = {
                    "id": row[0],
                    "text": row[1],
                    "type": row[2],
                    "chinese_translation": row[3]
                }
                details.append(detail)
            return details
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
   

def delete_word(word):
    connection = create_connection()
    try:
        with connection.cursor(buffered=True) as cursor:
            print(word)
            cursor.execute("SELECT id FROM word WHERE word=%s", (word,))
            result = cursor.fetchone()  # 使用 fetchone 来获取查询的结果
            if result is None:  # 检查是否查询到了结果
                print(f"No entry found for word: {word}")
                return
            word_id = result[0]  # 如果有结果，则获取 id 的值
            cursor.execute("DELETE FROM word_to_ra WHERE word_id=%s",(word_id,))
            cursor.execute("DELETE FROM word WHERE word=%s", (word,))
            connection.commit()
    except Error as e:
        print(f"Error occurred: {e}")
    finally:
        connection.close()
  


if __name__ == "__main__":
    setup_database()
    print(get_all_words())
    #print(get_word_details("unhappiness"))
    #print(get_root_or_affix_details())
