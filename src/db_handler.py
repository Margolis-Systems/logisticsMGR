from pymongo import MongoClient
from src import config


class Mongo:
    def __init__(self):
        self.con = MongoClient(config.con_str)
        self.db = self.con[config.db]

    def create_user(self, dic):
        for k in dic:
            if k not in config.user_items:
                del dic[k]
        self.db[config.users_col].update_one({'id': dic['id']}, {'$set': dic}, upsert=True)

    def validate_user(self, uid):
        ret = self.db[config.users_col].find_one({'id': uid}, {'_id': False})
        if ret:
            ret = dict(ret)
            ret['docs'] = list(self.db[config.docs_col].find({'to': uid}, {'_id': False}))
        return ret
