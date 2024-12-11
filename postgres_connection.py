import os
import psycopg2
import json
from datetime import datetime
from psycopg2 import Error
import logging

def sanitize_text(text):
    """
    Remove null characters and other potentially problematic characters from text.
    
    :param text: Input text to sanitize
    :return: Sanitized text
    """
    if text is None:
        return None
    
    # Convert to string if not already
    text_str = str(text)
    
    # Remove null characters
    text_cleaned = text_str.replace('\x00', '')
    
    # Optional: Remove other potentially problematic characters
    text_cleaned = text_cleaned.replace('\x0b', '')  # Vertical tab
    text_cleaned = text_cleaned.replace('\x0c', '')  # Form feed
    
    # Truncate extremely long text if needed
    return text_cleaned[:10000]  # Adjust max length as needed


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

                # Convert datetime objects to ISO format for all fields
                for item in data:
                    for key, value in item.items():
                        if isinstance(value, datetime):
                            item[key] = value.strftime("%Y-%m-%d %H:%M:%S.%f")

                # Serialize data to JSON
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



def connect_to_postgres(
    db_name=os.environ.get("DB_NAME", "mails"),
    db_user=os.environ.get("DB_USER", "root"),
    db_password=os.environ.get("DB_PASSWORD", "root"),
    db_host=os.environ.get("DB_HOST", "localhost"),
    db_port=int(os.environ.get("DB_PORT", "5432"))
):
    """
    Establish a connection to PostgreSQL database.
    
    :return: Database connection object
    """
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        return conn
    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None

def insert_email_to_postgres(conn, email_data):
    """
    Insert a single email message into PostgreSQL database.
    
    :param conn: PostgreSQL database connection
    :param email_data: Dictionary containing email message details
    :return: True if insertion successful, False otherwise
    """
    query = """
    INSERT INTO public.email_messages (
        sender_first_name, 
        sender_last_name, 
        receiver_first_name, 
        receiver_last_name,
        sender_email, 
        receiver_email, 
        sender_org, 
        receiver_org, 
        subject, 
        body, 
        date, 
        word_count, 
        summarised_body, 
        intent_category, 
        phone_numbers, 
        named_entities
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s
    );
    """
    
    # Helper function to split full name into first and last name
    def split_name(full_name):
        if not full_name:
            return None, None
        parts = str(full_name).split(maxsplit=1)
        return (parts[0], parts[1]) if len(parts) > 1 else (parts[0], None)
    
    # Helper function to sanitize text with a default value
    def safe_get(data, default=''):
        return sanitize_text(data) if data is not None else default
    
    # Prepare the parameters
    sender_first_name, sender_last_name = split_name(email_data.get('sender_name', ''))
    recipient_first_name, recipient_last_name = split_name(email_data.get('recipient_name', ''))
    
    # Parse date if it's a string
    date = email_data.get('date')
    if isinstance(date, str):
        try:
            # Parse the date with the new format
            date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            # Only log or print the error, don't replace with current time
            print(f"Could not parse date: {date}")
            date = None
    
    # Sanitize named entities
    sanitized_named_entities = {}
    if email_data.get('named_entities'):
        for category, entities in email_data['named_entities'].items():
            # Handle both list and string cases
            if isinstance(entities, list):
                sanitized_named_entities[category] = [safe_get(entity) for entity in entities]
            else:
                sanitized_named_entities[category] = safe_get(entities)
    
    # Default values or None if not present
    params = (
        sender_first_name,
        sender_last_name,
        recipient_first_name,
        recipient_last_name,
        safe_get(email_data.get('sender_email')),
        safe_get(email_data.get('recipient_email')),
        safe_get(email_data.get('sender_organization')),
        safe_get(email_data.get('recipient_organization')),
        safe_get(email_data.get('subject')),
        safe_get(email_data.get('body')),
        date,
        email_data.get('word_count', 0),
        None,  # summarised_body (optional)
        safe_get(email_data.get('intent')),
        [],  # phone_numbers (empty list if not provided)
        # Serialize sanitized named entities
        json.dumps(sanitized_named_entities) if sanitized_named_entities else None
    )
    
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
            return True
    except (Exception, psycopg2.Error) as error:
        conn.rollback()
        print(f"Error inserting email message: {error}")
        # Optional: log the problematic email data for debugging
        print("Problematic email data:", email_data)
        return False

def bulk_insert_emails(emails, db_path=None):
    """
    Insert multiple emails into PostgreSQL database.
    
    :param emails: List of email dictionaries
    :param db_path: Optional database path (not used in PostgreSQL)
    :return: Tuple of (successful insertions, total emails)
    """
    # Establish database connection
    conn = connect_to_postgres()
    if not conn:
        print("Failed to connect to database")
        return 0, len(emails)
    
    successful_inserts = 0
    total_emails = len(emails)
    failed_emails = []
    
    try:
        for email in emails:
            try:
                if insert_email_to_postgres(conn, email):
                    successful_inserts += 1
                else:
                    failed_emails.append(email)
            except Exception as email_error:
                print(f"Error processing individual email: {email_error}")
                failed_emails.append(email)
    except Exception as e:
        print(f"Error during bulk insertion: {e}")
    finally:
        conn.close()
    
    print(f"Inserted {successful_inserts} out of {total_emails} emails")
    if failed_emails:
        print(f"Failed to insert {len(failed_emails)} emails")
        # Optional: Log or save failed emails for later investigation
    
    return successful_inserts, total_emails

# If you want to use this as a standalone script
if __name__ == "__main__":
    # Placeholder for potential standalone testing
    pass
