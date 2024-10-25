from main import db_handle
from datetime import datetime


def sign(dic):
    if not db_handle.validate_user(dic['id']):
        db_handle.create_user(dic)
    # todo: from. id from session
    doc = {'from': '', 'to': dic['id'], 'date': datetime.now(), 'items': [], 'sign': False}
    for k in dic:
        if 'item' in k and dic[k]:
            # todo: 'cat'?
            doc['items'].append({'cat': '', 'description': dic[k], 'quantity': dic[k.replace('item', 'quantity')],
                                 'note': dic[k.replace('item', 'note')]})
    if doc['items']:
        db_handle.add_doc_to_sign(doc)


def ret(dic):
    # {'id': '7661862', '|0': '', '2024-10-21 20:36:56.281000|0': '2', '2024-10-21 20:55:12.775000|0': '',
    # '2024-10-22 09:10:58.122000|0': ''}
    for item in dic:
        q = item.split('|')
        if len(q) > 1 and dic[item]:
            date = q[0]
            index = int(q[1])
            quantity = int(dic[item])
            db_handle.return_item(dic['id'],date , index, quantity)
    return
