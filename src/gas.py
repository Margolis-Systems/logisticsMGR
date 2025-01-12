import os.path
import main
from datetime import datetime


def sign(dic, user, photo=None):
    qnt = int(dic['quantity'])
    if qnt <= 0:
        return
    doc_id = ts()
    doc = {'date': datetime.now(), 'doc_id': doc_id, 'sign': False}
    for k in dic:
        if k in ['id', 'name', 'last_name', 'rank', 'department', 'phone']:
            doc[k] = dic[k]
    if photo:
        doc['photo'] = doc_id
        if not os.path.exists('static/img/gas'):
            os.mkdir('static/img/gas')
        filename = 'static/img/gas/{}.jpeg'.format(doc_id)
        photo.save(filename)
    doc[dic['type']] = {dic['liter']: {'quantity': qnt}}
    if user['department'] == main.config.admin_department:
        doc['from'] = {'storage': 'gas'}
        main.db_handle.update_one('gas', {'storage': {'$exists': True}},
                                  {'$inc': {'{}.{}'.format(dic['type'], dic['liter']): -qnt}})
    else:
        doc['from'] = {}
        for k in ['id', 'name', 'last_name', 'rank', 'department', 'phone']:
            doc['from'][k] = user[k]
        temp = main.db_handle.read('gas', {'id': user['id'], '{}.{}'.format(dic['type'], dic['liter']): {'$exists': True}})
        for i in temp:
            if qnt <= i[dic['type']][dic['liter']]['quantity']:
                main.db_handle.update_one('gas', {'id': user['id'], 'doc_id': '12-01-2025_12-21-08', '{}.{}'.format(dic['type'], dic['liter']): {'$exists': True}},
                                          {'$inc': {'{}.{}.quantity'.format(dic['type'], dic['liter']): -qnt}})
                break
            else:
                qnt -= i[dic['type']][dic['liter']]['quantity']
                main.db_handle.update_one('gas', {'id': user['id'], 'doc_id': '12-01-2025_12-21-08',
                                                  '{}.{}'.format(dic['type'], dic['liter']): {'$exists': True}},
                                          {'$unset': {'{}.{}'.format(dic['type'], dic['liter'])}})
    main.db_handle.write_doc(doc, 'gas')


def ret(dic, user):
    pid = dic['id']
    for k in dic:
        if '|' in k:
            if dic[k]:
                ctype, litters, doc_id = k.split('|')
                quantity = -int(dic[k])
                main.db_handle.update_one('gas', {'id': pid, 'doc_id': doc_id},
                                          {'$inc': {'{}.{}.quantity'.format(ctype, litters): -quantity}})
                main.db_handle.update_one('gas', {'storage': {'$exists': True}},
                                          {'$inc': {'{}.{}'.format(ctype, litters): quantity}})
                if user['department'] != main.config.admin_department:
                    doc = user.copy()
                    data = {'type': ctype, 'liter': litters, 'quantity': quantity}
                    doc.update(data)
                    sign(doc, {'department': main.config.admin_department})


def ts():
    return datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
