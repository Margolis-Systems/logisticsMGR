import main
from datetime import datetime


def sign(dic, photo=None):
    doc_id = ts()
    doc = {'date': datetime.now(), 'items': [], 'doc_id': doc_id, 'sign': False}
    for k in dic:
        if k in ['id', 'name', 'last_name', 'rank', 'department', 'phone']:
            doc[k] = dic[k]
    if photo:
        doc['photo'] = doc_id
        filename = 'static/img/gas/{}.jpeg'.format(doc_id)
        photo.save(filename)
    for i in range(int(dic['quantity'])):
        new = {'serial': 0, 'type': dic['type']}
        if dic['serial_s'] and dic['serial_e']:
            new['serial'] = int(dic['serial_s'])+i
        doc['items'].append(new)
    if doc['items']:
        main.db_handle.write_doc(doc, 'gas')


def ret(dic):
    return


def ts():
    return datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
