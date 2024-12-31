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

    def validate_user(self, uid, phone, admin=False):
        query = {'id': uid, 'phone': phone, 'storage': {'$exists': False}}
        if admin:
            del query['phone']
            del query['storage']
        user = self.db[config.users_col].find_one(query, {'_id': False})
        if user:
            user = dict(user)
            user['docs'] = list(self.db[config.docs_col].find({'id': uid}, {'_id': False}))
            return user
        return {}

    def all_users(self):
        return list(self.db[config.users_col].find({}, {'_id': False}).sort([('department', 1), ('last_name', 1),
                                                                               ('name', 1)]))

    def read_list(self, list_name):
        return self.db[config.lists_col].find_one({'name': list_name}, {'_id': False})['list']

    def write_doc(self, doc, col=config.docs_col):
        self.db[col].update_one({'id': doc['id'], 'date': doc['date']}, {'$set': doc}, upsert=True)

    def sign_docs(self, uid):
        self.db[config.docs_col].update_many({'id': uid}, {'$set': {'sign': True}}, upsert=True)

    def return_item(self, person_id, date, index, quantity):
        date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        to_update = self.db[config.docs_col].find_one({'id': person_id, 'date': date})
        if not to_update:
            return
        if int(to_update['items'][index]['quantity']) <= quantity:
            del to_update['items'][index]
        else:
            to_update['items'][index]['quantity'] = str(int(to_update['items'][index]['quantity']) - quantity)
        if len(to_update['items']) > 0:
            self.db[config.docs_col].update_one({'id': person_id, 'date': date}, {'$set': {'items': to_update['items']}})
        else:
            self.db[config.docs_col].delete_one({'id': person_id, 'date': date})

    def read_docs(self, query=None, col=config.docs_col):
        if not query:
            query = {}
        return list(self.db[col].find(query, {'_id': False}).sort([('department', 1), ('last_name', 1),
                                                                               ('name', 1)]))

    def read_inv(self, query=None):
        if not query:
            query = {}
        all_inv = list(self.db[config.storage_col].find(query, {'_id': False}))
        inv = {}
        for ai in all_inv:
            for i in ai:
                if i != 'id':
                    if i not in inv:
                        inv[i] = ai[i]
                    else:
                        inv += ai[i]
        return inv

    def update_inv(self, items):
        for i in items:
            self.db[config.storage_col].update_one({},
                                                   {'$inc': {i['description']: i['quantity']}}, upsert=True)




