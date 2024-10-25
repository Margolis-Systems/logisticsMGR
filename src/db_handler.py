import datetime

from pymongo import MongoClient
from src import config


class Mongo:
    def __init__(self):
        self.con = MongoClient(config.con_str)
        self.db = self.con[config.db]

    def create_user(self, dic):
        new_dic = {}
        for k in dic:
            if k in config.user_items:
                new_dic[k] = dic[k]
        if new_dic:
            self.db[config.users_col].update_one({'id': dic['id']}, {'$set': new_dic}, upsert=True)

    def validate_user(self, uid):
        # todo: check cookie with secret
        ret = self.db[config.users_col].find_one({'id': uid}, {'_id': False})
        if ret:
            ret = dict(ret)
            ret['docs'] = list(self.db[config.docs_col].find({'to': uid}, {'_id': False}))
        return ret

    def read_list(self, list_name):
        return self.db[config.lists_col].find_one({'name': list_name}, {'_id': False})

    def add_doc_to_sign(self, doc):
        for item in doc['items']:
            if 'description' in item:
                if item['description'] not in config.descriptions:
                    config.descriptions.append(item['description'])
                    self.db[config.lists_col].update_one({'name': 'descriptions'}, {'$push': {'list': item['description']}})
        self.db[config.docs_col].update_one({'to': doc['to'], 'date': doc['date']}, {'$set': doc}, upsert=True)
        # todo: send SMS

    def return_item(self, person_id, date, index, quantity):
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        to_update = self.db[config.docs_col].find_one({'to': person_id, 'date': date})
        if int(to_update['items'][index]['quantity']) <= quantity:
            del to_update['items'][index]
        else:
            to_update['items'][index]['quantity'] = str(int(to_update['items'][index]['quantity']) - quantity)
        if len(to_update['items']) > 0:
            self.db[config.docs_col].update_one({'to': person_id, 'date': date}, {'$set': {'items': to_update['items']}})
        else:
            self.db[config.docs_col].delete_one({'to': person_id, 'date': date})
