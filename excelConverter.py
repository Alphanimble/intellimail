def export_features_to_excel(features_list, filename='features_export.xlsx'):
    # Create a dictionary with the required columns
    data = [
        {
            'Sender First Name': feature.sender_first_name,
            'Sender Last Name': feature.sender_last_name,
            'Receiver First Name': feature.reciever_first_name,
            'Receiver Last Name': feature.reciever_last_name,
            'Sender Email': feature.sender_email,
            'Receiver Email': feature.reciever_email,
            'organization' : feature.reciever_org,
            'phone number' : feature.phone_numbers
        }
        for feature in features_list
    ]

    # Create DataFrame
    df = pd.DataFrame(data)

    # Write to Excel file
    df.to_excel(filename, index=False)
export_features_to_excel(parsed_data_list)
