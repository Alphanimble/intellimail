from flask import Flask, request, render_template
import os
import json
import re
from email import policy
from email.parser import BytesParser
from mistralai import Mistral

# Initialize the Flask app
app = Flask(__name__)

# Initialize the Mistral client
mistral_client = Mistral(api_key='IzwdiP0W04dwKFs1hRB3Mex6yhqHjPVV')  # Replace with your API key
model = "mistral-large-latest"  # Specify your model name

# Set upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'eml'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for uploading files
@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return render_template('upload.html', error='No file part')
    
    file = request.files['file']

    # If the user does not select a file, the browser may submit an empty part without filename
    if file.filename == '':
        return render_template('upload.html', error='No selected file')
    
    if file and allowed_file(file.filename):
        # Save the uploaded file
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Check if the file is .eml or .txt and call corresponding method
        if file.filename.endswith('.eml'):
            parsed_data = parse_eml_file(filepath)
        elif file.filename.endswith('.txt'):
            parsed_data = parse_txt_file(filepath)
        else:
            return render_template('upload.html', error='Unsupported file format')

        # Build result string and summarize the text
        result_string = build_result_string(parsed_data)
        summary_output = summarize_and_classify_text(result_string)

        # Print the summary output to the terminal
        print("\nAPI Response:\n", summary_output)  # Print the API response in the terminal

        # Display results on the webpage
        return render_template('result.html', summary_output=summary_output, parsed_data=parsed_data)

    return render_template('upload.html', error='File type not allowed')

# Parsing function for .eml files
def parse_eml_file(filepath):
    parsed_data = {}

    # Parse the .eml file using BytesParser
    with open(filepath, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    # Extract headers
    parsed_data['Date'] = msg['Date']
    parsed_data['Subject'] = msg['Subject']
    parsed_data['From'] = msg['From']
    parsed_data['To'] = msg['To']
    parsed_data['Reply-To'] = msg['Reply-To']
    parsed_data['Message-ID'] = msg['Message-ID']

    # Extract the email body
    if msg.is_multipart():
        # If multipart, get the text/plain part
        for part in msg.iter_parts():
            if part.get_content_type() == 'text/plain':
                parsed_data['Unstructured-Text'] = part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
                break
    else:
        # If not multipart, get the payload (body)
        parsed_data['Unstructured-Text'] = msg.get_payload(decode=True).decode(msg.get_content_charset(), 'ignore')

    # Extract domain (mail server) from the "From" field
    if 'From' in parsed_data and parsed_data['From']:
        email_address = parsed_data['From']
        domain = email_address.split('@')[-1] if '@' in email_address else ''
        organization = domain.split('.')[0] if domain else ''
        parsed_data['Organization'] = organization
    print(parsed_data)
    return parsed_data

# Parsing function for .txt files with JSON-like structure
def parse_txt_file(filepath):
    parsed_data = {}

    # Read the file and parse it as JSON
    with open(filepath, 'r') as f:
        json_data = json.load(f)
    
    # Extract relevant fields
    message = json_data.get('message', '')
    
    # Use regex to extract headers and body from the "message" field
    parsed_data['Message-ID'] = extract_field(message, 'Message-ID')
    parsed_data['Date'] = extract_field(message, 'Date')
    parsed_data['From'] = extract_field(message, 'From')
    parsed_data['To'] = extract_field(message, 'To')
    parsed_data['Subject'] = extract_field(message, 'Subject')
    parsed_data['Unstructured-Text'] = extract_body_from_message(message)
    # Extract domain (mail server) from the "From" field
    if 'From' in parsed_data and parsed_data['From']:
        email_address = parsed_data['From']
        domain = email_address.split('@')[-1] if '@' in email_address else ''
        organization = domain.split('.')[0] if domain else ''
        parsed_data['Organization'] = organization
    print("\n\n\nParsed Message Data:\n")
    for key, value in parsed_data.items():
        print(f"{key}: {value}")
    return parsed_data

# Helper function to extract fields using regex
def extract_field(message, field_name):
    match = re.search(rf'{field_name}: (.+)', message)
    return match.group(1).strip() if match else ''

# Extract body from the message (after the headers)
def extract_body_from_message(message):
    body_start_index = message.find('\n\n')  # Look for the first occurrence of double newline
    return message[body_start_index + 2:].strip() if body_start_index != -1 else ""

def build_result_string(parsed_data):
    result_string = (
        f"\nMessage-ID: \t {parsed_data['Message-ID']}"
        f"\nFrom: \t {parsed_data['From']}"
        f"\nSubject: \t {parsed_data['Subject']}"
        f"\nDate: \t {parsed_data['Date']}"
        f"\nBody: \t {parsed_data['Unstructured-Text']}"
    )
    print("\n\nResult string:\n\n")
    print(result_string)
    return result_string

def summarize_and_classify_text(input_text):
    prompt = (
        f"Please summarize the following text into 20 words and provide a new subject. Classify the content as 'Spam', 'Important', or 'Other'."
        f"Do not use headings like new subject, summary, or classification. I need only 3 responses: Subject, Summary, and Classification, in that order, separated by 2 new lines."
        f"This is how I want the api response to be:\n<Subject>\n\n<Summary>\n\n<Classification>"
        f"Reply in plain text; do not use bold text:\n\n{input_text}"
    )

    chat_response = mistral_client.chat.complete(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    return chat_response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True)
