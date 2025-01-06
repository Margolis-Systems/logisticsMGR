from flask import Flask, render_template, redirect, request, make_response, stream_with_context, Response, session
from src import config, db_handler, inventory, sms_handler, gas, users
import secrets
from datetime import datetime, timedelta

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
                msg = 'פיקוד העורף - גדוד ניוד\nהוחתמת על ציוד באופן דיגיטלי.\nלצפיה, יש להכנס בקישור המצורף:\n\n{}'.format(
                    str(request.host_url))
                sms.send_sms(msg, [rf['phone']])
                return redirect('/sign')
            elif request.values:
                if 'id' in request.values:
                    pid = request.values['id']
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
                if len(rf.keys()) > 1:
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
            storages = db_handle.read_list('storage')
            return render_template('pages/sign_storage.html', user=user, data={'storages': storages})
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
                gas_store = db_handle.read_docs({'storage': True}, col='gas')
                docs = db_handle.read_docs({'storage': {'$exists': False}}, col='gas')
                if gas_store:
                    gas_store = gas_store[0]
                    del gas_store['storage']
                if request.form:
                    rf = dict(request.form)
                    print('gas main fr', rf)
                if 'page' in request.values:
                    page = request.values['page']
                    if page == 'sign':
                        return render_template('gas/gas_in.html', user=user, gas_store=gas_store)
                    elif page == 'ret':
                        return render_template('gas/gas_out.html', user=user, gas_store=gas_store)
                return render_template('gas/gas.html', user=user, gas_store=gas_store, docs=docs)
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
            users = db_handle.all_users()
            return render_template('gas/sign_gas.html', user=user, users=users)
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
                docs = db_handle.read_docs({'id': rf['id']}, 'gas')
                if not docs:
                    msg = 'לא נמצאו טפסים עבור {}'.format(rf['id'])
            if user['department'] == 'לוגיסטיקה':
                users = db_handle.all_users()
            else:
                users = db_handle.all_users({'department': user['department']})
            return render_template('gas/return_gas.html', user=user, data={'docs': docs, 'msg': msg}, users=users)
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
            if request.form:
                db_handle.create_user(dict(request.form))
                all_users = db_handle.all_users({'id': request.form['id']})[0]
                return render_template('pages/edit_person.html', user=user, users=all_users)
            elif 'delete' in request.values:
                user = users.validate_user(request.values['id'], '', True)
                if not user['docs']:
                    db_handle.delete_one('users', {'id': request.values['id']})
                else:
                    return redirect('/personal')
            elif 'id' in request.values:
                all_users = users.validate_user(request.values['id'],'',True)
                return render_template('pages/edit_person.html', user=user, users=all_users)
            all_users = db_handle.all_users()
            return render_template('pages/personal.html', user=user, users=all_users)
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
