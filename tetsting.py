from src import db_handler, config, sms_handler
import csv

db_handle = db_handler.Mongo()


def csv_to_mongo(csv_dir):
    with open(csv_dir, newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row[4].isnumeric():
                continue
            dic = {}
            for k in config.user_items:
                dic[k] = ''
            dic['id'] = row[4]
            dic['name'] = row[5].replace('*', "")
            dic['last_name'] = row[6]
            dic['rank'] = row[3]
            dic['phone'] = row[2].replace('-','')
            dic['department'] = row[1]
            if row[0]:
                dic['priv'] = True
            # db_handle.create_user(dic)


# csv_to_mongo("C:\\Users\\MargoliSys\\Downloads\\מצבת כח אדם - גיליון1.csv")
