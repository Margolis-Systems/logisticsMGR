from flask import Flask, render_template, redirect, request, make_response, session, send_from_directory, url_for
from src import config, db_handler, inventory, sms_handler, gas, users, file_handler
from datetime import datetime, timedelta
import os

sms = sms_handler.Sms()
db_handle = db_handler.Mongo()
app = Flask('Logistics')


@app.route('/', methods=['POST', 'GET'])
def main_page():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        s = db_handle.read_docs({'id': user['id'], 'sign': False})
        if s:
            s = True
        user['sign'] = s
        if request.form:
            rf = dict(request.form)
            if 'sign' in rf:
                if rf['sign'] == 'true':
                    db_handle.sign_docs(session['username'])
                    return redirect('/')
    else:
        return redirect('/login')
    return render_template('main.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    cookie_id = request.cookies.get('id')
    cookie_phone = request.cookies.get('phone')
    if request.form:
        # todo: second step token from sms
        req = dict(request.form)
        if 'id' in req and 'phone' in req:
            user = db_handle.validate_user(req['id'], req['phone'])
            # session['pass'] = secrets.token_urlsafe(16)
            if user:
                session['username'] = req['id']
                session['phone'] = req['phone']
                resp = make_response()
                resp.headers['location'] = '/'
                expire_date = datetime.now() + timedelta(days=60)
                resp.set_cookie('id', req['id'], expires=expire_date)
                resp.set_cookie('phone', req['phone'], expires=expire_date)
                return resp, 302
            else:
                msg = 'לא נמצאו תוצאות'
    elif cookie_id and cookie_phone:
        user = db_handle.validate_user(cookie_id, cookie_phone)
        if user:
            session['username'] = cookie_id
            session['phone'] = cookie_phone
            return redirect('/')
        else:
            msg = 'לא נמצאו תוצאות'
    return render_template('pages/login.html', data={'msg': msg})


@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    resp = make_response()
    resp.headers['location'] = '/'
    expire_date = datetime.now()
    resp.set_cookie('id', '', expires=expire_date)
    resp.set_cookie('phone', '', expires=expire_date)
    return resp, 302


@app.route('/get_info', methods=['POST', 'GET'])
def get_info():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            if user['department'] == config.admin_department:
                return db_handle.validate_user(request.values['id'], '', True)
    return {}


@app.route('/inv', methods=['POST', 'GET'])
def inv():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            if user['department'] == config.admin_department:
                if 'storage' in request.values:
                    all_inv = {'actual': db_handle.read_inv({}), 'total': {}}
                    docs = db_handle.read_docs({'storage': {'$exists': True}})
                    for d in docs:
                        for item in d['items']:
                            if item['description'] not in all_inv['total']:
                                all_inv['total'][item['description']] = int(item['quantity'])
                            else:
                                all_inv['total'][item['description']] += int(item['quantity'])
                    return render_template('pages/inventory.html', user=user, data={'inv': all_inv, 'docs': docs})
                docs = db_handle.read_docs({'storage': {'$exists': False}})
                return render_template('pages/doc.html', user=user, data=docs)
    return redirect('/')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            pid = ''
            if request.form:
                rf = dict(request.form)
                inventory.sign(rf, user)
                docs = db_handle.read_docs({'id': rf['id'], 'sign': False})
                if docs:
                    msg = 'הר ציון - גדוד צפון - לוגיסטיקה\n\nהנך חתומ.ה על הציוד:\n'
                    send = False
                    for doc in docs:
                        for item in doc['items']:
                            msg += "\n{} : {} יח'".format(item['description'], item['quantity'])
                            send = True
                    if send:
                        token = ''
                        # todo: gen and save token
                        msg += '\n\nלאישור לחץ:\n{}sms_sign?id={}&token={}'.format(str(request.host_url), rf['id'], token)
                        # sms.send_sms(msg, [rf['phone']])
                return redirect('/sign')
            elif request.values:
                if 'id' in request.values:
                    pid = request.values['id']
            items = get_items(user)
            return render_template('pages/sign.html', user=user, data={'items': items, 'id': pid}, users=db_handle.all_users())
    return redirect('/')


@app.route('/ret', methods=['POST', 'GET'])
def ret():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            docs = {}
            msg = ''
            rf = dict(request.form)
            if not rf and request.values:
                rf = dict(request.values)
            if rf:
                if 'ret' in rf:
                    inventory.ret(rf)
                if 'id' in rf:
                    docs = db_handle.read_docs({'id': rf['id']})
                    if not docs:
                        msg = 'לא נמצאו טפסים עבור {}'.format(rf['id'])
                    else:
                        docs.reverse()
                else:
                    docs['msg'] = 'ERROR'
            return render_template('pages/return.html', user=user, data={'docs': docs, 'msg': msg}, users=db_handle.all_users())
    return redirect('/')


@app.route('/sign_storage', methods=['POST', 'GET'])
def sign_storage():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            if request.form:
                rf = dict(request.form)
                rf['storage'] = ''
                inventory.sign(rf)
                return redirect('/sign_storage')
            return render_template('pages/sign_storage.html', user=user, data={'storages': [{'name': 'מחסן'}]})
    return redirect('/')


@app.route('/ret_storage', methods=['POST', 'GET'])
def ret_storage():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            docs = db_handle.read_docs({'storage': {'$exists': True}})
            if request.form:
                inventory.ret(dict(request.form), storage=True)
                return redirect('/ret_storage')
            return render_template('pages/return_storage.html', user=user, data={'docs': docs})
    return redirect('/')


@app.route('/gas', methods=['POST', 'GET'])
def gas_main():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            if user['department'] == 'לוגיסטיקה':
                if request.form:
                    rf = dict(request.form)
                    if 'type' in rf:
                        db_handle.update_one('gas', {'storage': {'$exists': True}}, {'$inc': {'{}.{}'.format(rf['type'], rf['liter']): int(rf['quantity'])}})
                    else:
                        for k in rf:
                            ctype, liter = k.split('|')

                            db_handle.update_one('gas', {'storage': {'$exists': True}}, {'$set': {'{}.{}'.format(ctype, liter): int(rf[k])}})
                gas_store = dict(db_handle.read_one('gas', {'storage': {'$exists': True}}))
                docs = db_handle.read_docs({'storage': {'$exists': False}}, col='gas')
                if gas_store:
                    del gas_store['storage']
                return render_template('gas/gas.html', user=user, gas_store=gas_store, docs=docs)
    return redirect('/')


@app.route('/sign_gas', methods=['POST', 'GET'])
def sign_gas():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        msg = ''
        if user:
            if request.form:
                rf = dict(request.form)
                photo = None
                if 'file' in request.files:
                    if request.files['file']:
                        photo = request.files['file']
                gas.sign(rf, photo)
                session['msg'] = '{} {} הוחתם בהצלחה'.format(rf['name'], rf['last_name'])
                return redirect('/sign_gas')
            elif 'msg' in session:
                msg = session['msg']
                del session['msg']
                session.modified = True
            all_users = db_handle.all_users()
            if user['department'] == config.admin_department:
                gas_store = dict(db_handle.read_one('gas', {'storage': {'$exists': True}}))
                if gas_store:
                    del gas_store['storage']
            else:
                gas_store = {}
                temp = db_handle.read('gas', {'id': session['username']})
                for i in temp:
                    for k in i:
                        if isinstance(i[k], dict):
                            if k not in gas_store:
                                gas_store[k] = {}
                            for li in i[k]:
                                if li not in gas_store[k]:
                                    gas_store[k][li] = 0
                                gas_store[k][li] += i[k][li]['quantity']
            return render_template('gas/sign_gas.html', user=user, users=all_users, msg=msg, gas_store=gas_store)
    return redirect('/')


@app.route('/ret_gas', methods=['POST', 'GET'])
def ret_gas():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            docs = {}
            msg = ''
            rf = dict(request.form)
            if not rf and request.values:
                rf = dict(request.values)
            if rf:
                if len(rf.keys()) > 1:
                    gas.ret(dict(request.form))
                    return redirect('/ret_gas?id={}'.format(rf['id']))
                docs = db_handle.read_docs({'id': rf['id']}, 'gas')
                if not docs:
                    msg = 'לא נמצאו טפסים עבור {}'.format(rf['id'])
            if user['department'] == 'לוגיסטיקה':
                all_users = db_handle.all_users()
            else:
                all_users = db_handle.all_users({'department': user['department']})
            return render_template('gas/return_gas.html', user=user, data={'docs': docs, 'msg': msg}, users=all_users)
    return redirect('/')


@app.route('/init')
def init(force=False):
    if not force:
        if 'username' in session and 'phone' in session:
            user = db_handle.validate_user(session['username'], session['phone'])
            if user:
                if user['department'] != config.admin_department:
                    return
            else:
                return
    config.dictionary = db_handle.read_list('dictionary')
    config.doc_items = db_handle.read_list('doc_items')
    config.user_items = db_handle.read_list('user_items')


@app.route('/personal', methods=['POST', 'GET'])
def personal():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            items = get_items(user)
            if request.form:
                rf = dict(request.form)
                db_handle.create_user(rf)
                # if 'action' in rf:
                #     if rf['action'] == 'sign':
                #         inventory.sign(rf, user)
                #         docs = db_handle.read_docs({'id': rf['id']})
                #         if docs:
                #             msg = 'פיקוד העורף - גדוד ניוד\nהוחתמת על ציוד באופן דיגיטלי.\n'
                #             send = False
                #             for doc in docs:
                #                 for item in doc['items']:
                #                     msg += '\n{} : {} יח'.format(item['description'], item['quantity'])
                #                     send = True
                #             if send:
                #                 token = ''
                #                 # todo: gen and save token
                #                 msg += '\nלאישור לחץ:\n{}sms_sign?id={}&token={}'.format(str(request.host_url), rf['id'], token)
                #                 # sms.send_sms(msg, [rf['phone']])
                all_users = users.validate_user(request.values['id'], '', True)
                return render_template('pages/edit_person.html', user=user, users=all_users, data={'items': items})
            elif 'delete' in request.values:
                user = users.validate_user(request.values['id'], '', True)
                if not user['docs']:
                    db_handle.delete_one('users', {'id': request.values['id']})
                else:
                    return redirect('/personal')
            elif 'id' in request.values:
                all_users = users.validate_user(request.values['id'], '', True)
                return render_template('pages/edit_person.html', user=user, users=all_users, data={'items': items})
            all_users = db_handle.all_users()
            return render_template('pages/personal.html', user=user, users=all_users)
    return redirect('/')


@app.route('/sms_sign', methods=['GET'])
def sms_sign():
    msg = ''
    if 'id' in request.values:
        # todo: validate token
        docs = db_handle.read_docs({'id': request.values['id'], 'sign': False})
        if docs:
            db_handle.sign_docs(request.values['id'])
            msg = 'חתימה התקבלה בהצלחה'
        else:
            msg = ''
    return render_template('pages/sms_sign.html', msg=msg)


@app.route('/download', methods=['GET', 'POST'])
def download():
    rv = dict(request.values)
    if rv:
        if 'csv' in rv:
            if 'storage' in rv:
                headers = ['name', 'description', 'quantity', 'note', 'in_stock']
                query = {'storage': {'$exists': True}}
                file_name = 'inventory'
            else:
                headers = ['name', 'last_name', 'id', 'department', 'description', 'quantity', 'note']
                file_name = 'signed'
                query = {'storage': {'$exists': False}}
            docs = db_handle.read_docs(query)
            if docs:
                data = []
                for d in docs:
                    info = {}
                    keys = ['id', 'name', 'last_name', 'department']
                    for k in keys:
                        if k in d:
                            info[k] = d[k]
                    for i in d['items']:
                        i.update(info)
                        data.append(i)
                file = file_handler.EXCEL.create_xlsx('static/csv/{}.xlsx'.format(file_name), data, headers)
                # file = file_handler.CSV.create_csv('static/csv/{}.csv'.format(file_name), data, headers)
                return send_from_directory(os.path.dirname(file), os.path.basename(file), as_attachment=True, mimetype="Content-Type: text/csv; charset=utf-8")
    return '', 204


def get_items(user):
    items = {}
    print(user)
    if user['department'] == config.admin_department:
        items = db_handle.read_inv()
    else:
        for d in user['docs']:
            for i in d['items']:
                if i['description'] not in items:
                    items[i['description']] = i['quantity']
                else:
                    items[i['description']] += i['quantity']
    print(items)
    return items


if __name__ == '__main__':
    # Initialize
    # Run App
    app.secret_key = '!afD345eW%##$'
    app.run(host="0.0.0.0", port=config.server_port, debug=True)

'''
כרטיסי דלק
מלל נפתח\נסגר

חיפוש במלאי לפי פריטים \ יחידה מספקת

ציוד מתקלה
'''
