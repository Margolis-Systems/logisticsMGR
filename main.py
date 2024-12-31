from flask import Flask, render_template, redirect, request, make_response, stream_with_context, Response, session
from src import config, db_handler, inventory, sms_handler, gas
import secrets
from datetime import datetime

sms = sms_handler.Sms()
db_handle = db_handler.Mongo()
app = Flask('Logistics')


@app.route('/', methods=['POST', 'GET'])
def main_page(page='', data=None):
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
        user = {}
        page = ''
        data = None
    return render_template('main.html', data=data, user=user, page=page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.form:
        # todo: second step token from sms
        req = dict(request.form)
        if 'id' in req and 'phone' in req:
            user = db_handle.validate_user(req['id'], req['phone'])
            session['username'] = req['id']
            session['phone'] = req['phone']
            # session['pass'] = secrets.token_urlsafe(16)
            if user:
                return redirect('/')
    return main_page(data={'msg': 'לא נמצאו תוצאות'})


@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect('/')


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
                    return main_page(page='pages/inventory.html', data={'inv': all_inv, 'docs': docs})
                docs = db_handle.read_docs({'storage': {'$exists': False}})
                return main_page(page='pages/doc.html', data=docs)
    return redirect('/')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            if request.form:
                rf = dict(request.form)
                inventory.sign(rf, user)
                msg = 'פיקוד העורף - גדוד ניוד\nהוחתמת על ציוד באופן דיגיטלי.\nלצפיה, יש להכנס בקישור המצורף:\n\n{}'.format(
                    str(request.host_url))
                sms.send_sms(msg, [rf['phone']])
                return redirect('/sign')
            items = {}
            if user['department'] == config.admin_department:
                items = db_handle.read_inv()
            else:
                for d in user['docs']:
                    for i in d['items']:
                        if i['description'] not in items:
                            items[i['description']] = i['quantity']
                        else:
                            items[i['description']] += i['quantity']
            return main_page(page='pages/sign.html', data={'items': items})
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
                if len(rf.keys()) > 1:
                    inventory.ret(rf)
                    return redirect('/ret')
                elif 'id' in rf:
                    docs = db_handle.read_docs({'id': rf['id']})
                    if not docs:
                        msg = 'לא נמצאו טפסים'
                else:
                    docs['msg'] = 'ERROR'
            return main_page(page='pages/return.html', data={'docs': docs, 'msg': msg})
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
            storages = db_handle.read_list('storage')
            return main_page(page='pages/sign_storage.html', data={'storages': storages})
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
            return main_page(page='pages/return_storage.html', data={'docs': docs})
    return redirect('/')


@app.route('/sign_gas', methods=['POST', 'GET'])
def sign_gas():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            if request.form:
                photo = None
                if 'file' in request.files:
                    if request.files['file']:
                        photo = request.files['file']
                gas.sign(dict(request.form), photo)
                return redirect('/sign_gas')
            return main_page(page='pages/sign_gas.html')
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
                    return redirect('/ret_gas')
                elif 'id' in rf:
                    docs = db_handle.read_docs({'id': rf['id']}, 'gas')
                    if not docs:
                        msg = 'לא נמצאו טפסים'
                else:
                    docs['msg'] = 'ERROR'
            return main_page(page='pages/return_gas.html', data={'docs': docs, 'msg': msg})
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
    config.descriptions = db_handle.read_list('descriptions')
    config.dictionary = db_handle.read_list('dictionary')
    config.doc_items = db_handle.read_list('doc_items')
    config.user_items = db_handle.read_list('user_items')


@app.route('/personal')
def personal():
    if 'username' in session and 'phone' in session:
        user = db_handle.validate_user(session['username'], session['phone'])
        if user:
            all_users = db_handle.all_users()
            return render_template('pages/personal.html', users=all_users, user=user)
    return redirect('/')


if __name__ == '__main__':
    # Initialize
    init(True)
    # Run App
    app.secret_key = '!afD345eW%##$'
    app.run(host="0.0.0.0", port=config.server_port, debug=True)

'''
כרטיסי דלק
מלל נפתח\נסגר

חיפוש במלאי לפי פריטים \ יחידה מספקת

ציוד מתקלה
'''
