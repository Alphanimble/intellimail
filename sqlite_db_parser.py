import sqlite3
import spacy_parser_layer
import classyTest
import re
import postgres_connection

pconn = postgres_connection.connect_to_postgres()
if pconn:
    print("connected")
def parse_email_address(email_string):
    """
    Parse email address string into components.
    
    :param email_string: String containing name and email
    :return: Dictionary with name, email, and organization
    """
    # Regex to match name and email
    pattern = r'^(.*?)\s*<([^>]+)>$'
    
    # Default return if no match
    result = {
        'name': email_string,
        'email': email_string,
        'organization': ''
    }
    
    # Try to match the pattern
    match = re.match(pattern, email_string)
    if match:
        name = match.group(1).strip()
        email = match.group(2).strip()
        
        result['name'] = name
        result['email'] = email
        
        # Extract organization (if not gmail or outlook)
        org_match = re.search(r'@([^.]+)\.[a-z]+$', email, re.IGNORECASE)
        if org_match:
            org = org_match.group(1)
            # Ignore common email providers
            if org.lower() not in ['gmail', 'outlook', 'hotmail', 'yahoo']:
                result['organization'] = org.capitalize()
    
    return result

def extract_complete_email_data(db_path):
    global pconn
    """
    Extract complete email data from a SQLite database with enhanced parsing.
    
    :param db_path: Path to the SQLite database
    :return: List of complete email dictionaries
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Comprehensive SQL query to get all email data with matching IDs
    query = """
    SELECT 
        f.value AS from_field,
        t.value AS to_field,
        s.value AS subject,
        m.date AS date,
        m.body,
        m.id AS message_id
    FROM 
        message m
    LEFT JOIN 
        header_field f ON f.message_id = m.id AND f.header_field_type_id = 67
    LEFT JOIN 
        header_field t ON t.message_id = m.id AND t.header_field_type_id = 136
    LEFT JOIN 
        header_field s ON s.message_id = m.id AND s.header_field_type_id = 131
    WHERE 
        m.body IS NOT NULL 
        AND f.value IS NOT NULL 
        AND t.value IS NOT NULL 
        AND s.value IS NOT NULL
    """

    cur.execute(query)
    
    # Convert results to list of dictionaries
    columns = ['from', 'to', 'subject', 'date', 'body', 'message_id']
    emails = []
    for row in cur.fetchall():
        # Create email dictionary
        email_dict = dict(zip(columns, row))
        
        # Parse sender and recipient details
        sender = parse_email_address(email_dict['from'])
        recipient = parse_email_address(email_dict['to'])
        intent = classyTest.categorize_text(email_dict['body'])
        named_entities = spacy_parser_layer.get_entities(email_dict['body']) 
        word_count = spacy_parser_layer.get_word_count(email_dict['body'])
        # Update email dictionary with parsed details
        email_dict.update({
            'sender_name': sender['name'],
            'sender_email': sender['email'],
            'sender_organization': sender['organization'],
            'recipient_name': recipient['name'],
            'recipient_email': recipient['email'],
            'recipient_organization': recipient['organization'],
            'intent': intent,
            'named_entities':named_entities,
            'word_count':word_count,
        })
        # print(email_dict)
        emails.append(email_dict)
        postgres_connection.insert_email_to_postgres(pconn, email_dict)


    # Close connection
    conn.close()

    return emails

def main():
    # Extract emails from both databases
    emails_2018 = extract_complete_email_data('emails-2018.sqlite3')
    emails_2019 = extract_complete_email_data('emails-2019.sqlite3')
    for key in emails_2018[0].keys():
        print(key)
    # Print summary
    print(f"Emails from 2018 database: {len(emails_2018)}")
    print(f"Emails from 2019 database: {len(emails_2019)}")

    # Optional: Print some sample data
    def print_sample_emails(emails, db_name):
        print(f"\nSample emails from {db_name}:")
        for email in emails[:5]:
            print("\n--- Email ---")
            print(f"Sender: {email['sender_name']} <{email['sender_email']}> (Org: {email['sender_organization'] or 'N/A'})")
            print(f"Recipient: {email['recipient_name']} <{email['recipient_email']}> (Org: {email['recipient_organization'] or 'N/A'})")
            print(f"Date: {email['date']}")
            print(f"Subject: {email['subject']}")
            print(f"Intent: {email['intent']}")
            print(f"named_entities: {email['named_entities']}")
            print(f"word_count: {email['word_count']}")
            print(f"Message ID: {email['message_id']}")

    print_sample_emails(emails_2018, '2018')
    print_sample_emails(emails_2019, '2019')

    return emails_2018, emails_2019

if __name__ == "__main__":
    emails_2018, emails_2019 = main()
