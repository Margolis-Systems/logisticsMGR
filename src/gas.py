import os.path

import main
from datetime import datetime


def sign(dic, photo=None):
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
    main.db_handle.write_doc(doc, 'gas')
    # todo update inv


def ret(dic):
    print(dic)
    return


def ts():
    return datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
