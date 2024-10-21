import os
import psycopg2
from psycopg2 import Error
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
DB_NAME = os.environ.get('DB_NAME', 'mails')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))

def connect_to_db(db_name, db_user, db_password, db_host='localhost', db_port=5432):
    try:
        # Construct the connection string
        connection_string = f"dbname='{db_name}' user='{db_user}' password='{db_password}' host='{db_host}' port={db_port}"
        
        # Connect to the database
        conn = psycopg2.connect(connection_string)
        
        print("Successfully connected to the database.")
        return conn
    
    except (Exception, Error) as error:
        print(f"An error occurred while connecting to the database: {error}")
        return None

def execute_query(conn, query):
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()
            if cur.description:
                return cur.fetchall()
            else:
                # No results returned (e.g., INSERT, UPDATE, DELETE)
                return None
    except (Exception, Error) as error:
        logging.error(f"Error executing query: {error}")
        conn.rollback()
        raise
    finally:
        cur.close()

def main():
    try:
        # Establish connection
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        if conn:
            print("db connected")
        
        # Create a table
        # columns = [('name', 'VARCHAR(100)'), ('email', 'VARCHAR(100) UNIQUE NOT NULL')]
        # create_table(conn, "users", columns)
        # logging.info("Table created successfully")
        #
        # # Insert data into the table
        # insert_data(conn, "users", {"name": "John Doe", "email": "joh@example.com"})
        # logging.info("Data inserted successfully")
        #
        # Query the table
    except (Exception, Error) as error:
        logging.error(f"Error occurred: {error}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    main()
