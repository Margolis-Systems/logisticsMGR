from src import db_handler, config, sms_handler
import csv

db_handle = db_handler.Mongo()
# sms = sms_handler.Sms()

def csv_to_mongo(csv_dir):
    with open(csv_dir, newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if db_handle.validate_user(row[4]) or not row[4].isnumeric():
                continue
            dic = {}
            for k in config.user_items:
                dic[k] = ''
            dic['id'] = row[4]
            dic['name'] = row[5].replace('*', "")
            dic['last_name'] = row[6]
            db_handle.create_user(dic)
csv_to_mongo("C:\\Users\\MargoliSys\\Downloads\\מצבת כח אדם - גיליון1.csv")