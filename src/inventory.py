import main
from datetime import datetime


def sign(dic):
    if not main.db_handle.validate_user(dic['id']):
        main.db_handle.create_user(dic)
    # todo: from. id from session
    doc = {'from': '', 'to': dic['id'], 'date': datetime.now(), 'items': [], 'sign': False}
    for k in dic:
        if 'item' in k and dic[k]:
            # todo: 'cat'?
            doc['items'].append({'cat': '', 'description': dic[k], 'quantity': dic[k.replace('item', 'quantity')],
                                 'note': dic[k.replace('item', 'note')]})
    if doc['items']:
        main.db_handle.add_doc_to_sign(doc)


def ret(dic):
    print(dic)
    return
