import re

def extract_body(text):
    pattern = r'X-FileName:\s*([^>]+)'
    match = re.search(pattern, text, re.MULTILINE)
    
    if match:
        # Extract the content after X-FileName:
        content = match.group(1)
        
        # Split the content into lines and remove the first line
        lines = content.split('\n')
        if len(lines) > 1:
            # If there's more than one line, remove the first line
            content = '\n'.join(lines[1:])
        else:
            # If there's only one line, leave it as is
            pass
        
        return content
    else:
        return None
def extract_message_id(text):
    pattern = r'^Message-ID:\s*<([^>]+)>'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_date(text):
    pattern = r'Date:\s*(.*?)\n'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_sender_email(text):
    pattern = r'From:\s*(.*?)\n'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_sender_full_name(text):
    pattern = r'X-From:\s*(.*?)\n'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_reciever_full_name(text):
    pattern = r'X-To:\s*(.*?)\n'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_reciever_email(text):
    pattern = r'To:\s*(.*?)\n'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_subject(text):
    pattern = r'Subject:\s*(.*)$'
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1) if match else None

def extract_organization(email):
    pattern = r'@(.+).com'
    match = re.search(pattern, email)
    return match.group(1) if match else None

def extract_sender_org(email_text):
    sender_email = extract_sender_email(email_text)
    return extract_organization(sender_email) if sender_email else None

def extract_reciever_org(email_text):
    recipient_email = extract_reciever_email(email_text)
    return extract_organization(recipient_email) if recipient_email else None

def extract_phone_numbers(text):
    # Regex pattern to match phone numbers
    pattern = r'\+?\d{0,3}[-\s]?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}(?: *x\d+)?'
    # Find all matches in the text
    phone_numbers = re.findall(pattern, text)
    
    return phone_numbers



# Example usage
email_text = """Message-ID: <18782981.1075855378110.JavaMail.evans@thyme>
Date: Mon, 14 May 2001 16:39:00 -0700 (PDT)
From: phillip.allen@enron.com
To: tim.belden@rnron.com
Subject: this is a sample subject lol
Mime-Version: 1.0
Content-Type: text/plain; charset=us-ascii
Content-Transfer-Encoding: 7bit
X-From: Phillip K Allen
X-To: Tim Belden <Tim Belden/Enron@EnronXGate>
X-cc: 
X-bcc: 
X-Folder: \Phillip_Allen_Jan2002_1\Allen, Phillip K.\'Sent Mail
X-Origin: Allen-P
X-FileName: pallen (Non-Privileged).pst

this is the part of the message i need 
this +91 713-853-7107
123-456-7890
Here is our forecast "\nMr. Buckner,\n\n For delivered gas behind San Diego, Enron Energy Services is the appropriate \nEnron entity.  I have forwarded your request to Zarin Imam at EES.  Her phone \nnumber is 
713-853-7107
.  \n\nPhillip Allen"


"""
