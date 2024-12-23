from main import db_handle
from datetime import datetime


def sign(dic):
    db_handle.create_user(dic)
    doc = {'date': datetime.now(), 'items': [], 'sign': False}
    for k in dic:
        if 'item' in k and dic[k]:
            # todo: 'cat'?
            doc['items'].append({'cat': '', 'description': dic[k], 'quantity': dic[k.replace('item', 'quantity')],
                                 'note': dic[k.replace('item', 'note')]})
        elif k in ['id', 'name', 'last_name', 'department']:
            doc[k] = dic[k]
    if doc['items']:
        db_handle.add_doc_to_sign(doc)
        return True
    return False


def ret(dic):
    keys = list(dic.keys())
    keys.sort(reverse=True)
    for item in keys:
        q = item.split('|')
        if len(q) > 1 and dic[item]:
            date = q[0]
            index = int(q[1])
            quantity = int(dic[item])
            db_handle.return_item(dic['id'],date , index, quantity)
