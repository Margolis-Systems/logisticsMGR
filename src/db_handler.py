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

    def add_doc_to_sign(self, doc):
        self.db[config.docs_col].update_one({'to': doc['to'], 'date': doc['date']}, {'$set': doc}, upsert=True)
        # todo: send SMS
