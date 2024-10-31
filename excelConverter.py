import pandas as pd


def export_features_to_excel(features_list, filename="features_export.xlsx"):
    # Create a dictionary with the required columns
    data = [
        {
            "Sender First Name": feature.sender_first_name,
            "Sender Last Name": feature.sender_last_name,
            "Sender Email": feature.sender_email,
            "organization": feature.sender_org,
            "phone number": feature.phone_numbers,
            "Subject": feature.subject,
            "intent": feature.intent_category,
        }
        for feature in features_list
    ]

    # Create DataFrame
    df = pd.DataFrame(data)

    # Write to Excel file
    df.to_excel(filename, index=False)
