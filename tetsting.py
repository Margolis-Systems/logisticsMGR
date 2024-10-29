from src import db_handler, config, sms_handler
import csv

db_handle = db_handler.Mongo()
sms = sms_handler.Sms()

def csv_to_mongo(csv_dir):
    with open(csv_dir, newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if db_handle.validate_user(row[0]):
                continue
            dic = {}
            for k in config.user_items:
                dic[k] = ''
            dic['id'] = row[0]
            dic['name'] = row[1].replace('*', "")
            dic['last_name'] = row[2]
            db_handle.create_user(dic)
