import pandas as pd
import features
import regexParser
import excelConverter
import mongoPusher
import spacy_parser_layer
import postgres_connection
import classyTest

df = pd.read_csv("data.csv")
emailDf = pd.DataFrame(df.iloc[:, 1])
emailDf.to_csv("emails.csv", index=False)
parsed_data_list = []

for index, row in emailDf.iterrows():
    obj = features.Features()
    obj.message_id = regexParser.extract_message_id(row["message"])
    obj.subject = regexParser.extract_subject(row["message"])
    obj.reciever_email = regexParser.extract_sender_email(row["message"])
    obj.sender_email = regexParser.extract_reciever_email(row["message"])
    obj.reciever_org = regexParser.extract_sender_org(row["message"])
    obj.sender_org = regexParser.extract_reciever_org(row["message"])
    obj.body = regexParser.extract_body(row["message"])
    obj.date = regexParser.extract_date(row["message"])
    obj.reciever_full_name = regexParser.extract_sender_full_name(row["message"])
    obj.sender_full_name = regexParser.extract_reciever_full_name(row["message"])
    obj.phone_numbers = regexParser.extract_phone_numbers(obj.body)
    obj.populate_name()
    parsed_data_list.append(obj)

spacy_parser_layer.process_features(parsed_data_list)

for obj in parsed_data_list:
    obj.intent_category = classyTest.categorize_mail(obj)

excelConverter.export_features_to_excel(parsed_data_list)


# mongoPusher.convert_to_json(parsed_data_list)

conn = postgres_connection.connect_to_db("mails", "root", "root")
if conn:
    print("connected")
    for i in parsed_data_list:
        postgres_connection.add_mail_row(conn, i)
