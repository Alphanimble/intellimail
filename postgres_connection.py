import os
import json
from datetime import datetime
import psycopg2
from psycopg2 import Error
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Database configuration
DB_NAME = os.environ.get("DB_NAME", "mails")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "root")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))


def connect_to_db(db_name, db_user, db_password, db_host="localhost", db_port=5432):
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


def execute_query(conn, query, params=None):
    try:
        with conn.cursor() as cur:
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            conn.commit()
            if cur.description:
                rows = cur.fetchall()
                column_names = [desc[0] for desc in cur.description]
                data = [dict(zip(column_names, row)) for row in rows]

                # Convert datetime objects to ISO format
                for item in data:
                    if "date" in item and isinstance(item["date"], datetime):
                        item["date"] = item["date"].strftime("%a, %d %b %Y %H:%M:%S %z")

                json_data = json.dumps(data)
                return json_data
            else:
                # No results returned (e.g., INSERT, UPDATE, DELETE)
                return None
    except (Exception, Error) as error:
        logging.error(f"Error executing query: {error}")
        conn.rollback()
        raise
    finally:
        cur.close()


def add_mail_row(conn, obj):
    query = """
        INSERT INTO public.email_messages (
            sender_first_name, sender_last_name, receiver_first_name, receiver_last_name,
            sender_email, receiver_email, sender_org, receiver_org, subject, body, date, message_id,
            word_count, summarised_body, intent_category, phone_numbers, named_entities
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TO_TIMESTAMP(%s, 'Dy DD Mon YYYY HH24:MI:SS'), %s, %s, %s, %s, %s, %s
        );
    """
    params = (
        obj.sender_first_name,
        obj.sender_last_name,
        obj.reciever_first_name,
        obj.reciever_last_name,
        obj.sender_email,
        obj.reciever_email,
        obj.sender_org,
        obj.reciever_org,
        obj.subject,
        obj.body,
        obj.date,
        obj.message_id,
        obj.word_count,
        obj.summarised_body,
        obj.intent_category,
        obj.phone_numbers if isinstance(obj.phone_numbers, list) else [],
        json.dumps(obj.named_entities) if obj.named_entities else [],
    )
    res = execute_query(conn, query, params)


def main():
    try:
        # Establish connection
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
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
