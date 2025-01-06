from src import config, db_handler
mongo = db_handler.Mongo()


def create_user(dic):
    new_dic = {}
    for k in dic:
        if k in config.user_items:
            new_dic[k] = dic[k]
    if new_dic:
        mongo.update_one(config.users_col, {'id': dic['id']}, {'$set': new_dic}, upsert=True)


def validate_user(uid, phone, admin=False):
    query = {'id': uid, 'phone': phone, 'storage': {'$exists': False}}
    if admin:
        del query['phone']
        del query['storage']
    user = mongo.read_one(config.users_col, query)
    if user:
        user = dict(user)
        user['docs'] = list(mongo.read_one(config.docs_col, {'id': uid}))
        return user
    return {}


def all_users(query=None):
    if query is None:
        query = {}
    return list(mongo.read(config.users_col, query, sort=[('department', 1), ('last_name', 1), ('name', 1)]))


def remove_users(uid):
    for i in uid:
        user = validate_user(i, '', True)
        if 'docs' in user:
            if user['docs']:
                return
        mongo.delete_one(config.users_col, {'id': i})

