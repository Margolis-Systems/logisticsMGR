import main
from datetime import datetime


def sign(dic, from_user=None):
    inv = main.db_handle.read_inv()
    if 'add_new' in dic:
        if dic['add_new'] == 'true':
            main.db_handle.create_user(dic)
    doc = {'date': datetime.now(), 'items': [], 'sign': False}
    for k in dic:
        if 'item' in k and dic[k]:
            # todo: 'cat'?
            item = {'cat': '', 'description': dic[k], 'quantity': int(dic[k.replace('item', 'quantity')]),
                    'note': dic[k.replace('item', 'note')]}
            doc['items'].append(item)
        elif k in ['id', 'name', 'last_name', 'department'] and 'storage' not in dic:
            if 'from' not in doc:
                del from_user['docs']
                if 'token' in from_user:
                    del from_user['token']
                doc['from'] = from_user
            doc[k] = dic[k]
        elif k in ['name', 'last_name', 'rank', 'department', 'phone'] and 'storage' in dic:
            if 'from' not in doc:
                doc['from'] = {}
                storages = main.db_handle.read_list('storage')
                for s in storages:
                    if s['name'] == dic['storage']:
                        doc.update(s)
                        break
            doc['from'][k] = dic[k]
    if doc['items']:
        main.db_handle.write_doc(doc)
        for i in range(len(doc['items'])):
            if 'storage' not in dic:
                doc['items'][i]['quantity'] *= -1
                # if doc['items'][i]['description'] in inv.keys():
                #     doc['items'][i]['quantity'] *= -1
                # else:
                #     sign_store = doc.copy()
                #     sign_store['storage'] = True
                #     sign_store['id'] = '0'
                #     sign_store['name'] = 'מחסן'
                #     sign_store['items'] = [doc['items'][i]]
                #     main.db_handle.write_doc(sign_store)
                #     doc['items'][i]['quantity'] = 0
        main.db_handle.update_inv(doc['items'])


def ret(dic, storage=False):
    for k in dic:
        pid = dic['id']
        if k in ['id', 'name', 'last_name']:
            continue
        elif dic[k]:
            date, description, idx = k.split('|')
            qnt = int(dic[k])
            main.db_handle.return_item(pid, date, int(idx), qnt)
            if storage:
                qnt *= -1
            main.db_handle.update_inv([{'description': description, 'quantity': qnt}])
