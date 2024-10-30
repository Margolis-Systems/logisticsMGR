from flask import Flask, render_template, redirect, request, make_response, stream_with_context, Response, session
from src import config, db_handler, inventory, sms_handler
import secrets

sms = sms_handler.Sms()
db_handle = db_handler.Mongo()
app = Flask('Logistics')


@app.route('/', methods=['POST', 'GET'])
def main_page():
    data = {}
    msg = ''
    if request.form:
        data = db_handle.validate_user(request.form['id'])
        session['username'] = request.form['id']
        # session['pass'] = secrets.token_urlsafe(16)
        if not data:
            msg = 'לא נמצאו תוצאות'
    elif 'username' in session:
        data = db_handle.validate_user(session['username'])
    return render_template('main.html', data=data, doc_items=config.doc_items, msg=msg, dictionary=config.dictionary,
                           page_data={'department':config.admin_department})


@app.route('/close', methods=['GET'])
def close():
    return render_template('popup/close.html')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    if 'username' in session:
        user = db_handle.validate_user(session['username'])
        if user:
            if user['department'] == config.admin_department:
                r_v = request.values
                msg = ''
                data = {}
                if request.form or 'id' in r_v:
                    r_f = dict(request.form)
                    if 'return' in r_v:
                        inventory.ret(r_f)
                        if 'id' in r_f:
                            data = db_handle.validate_user(r_f['id'])
                            if not data:
                                data = {'docs': ''}
                            if not data['docs']:
                                msg = 'לא נמצאו טפסים לזיכוי'
                        elif 'id' in r_v:
                            data = db_handle.validate_user(r_v['id'])
                            if not data:
                                data = {'docs': ''}
                            if not data['docs']:
                                msg = 'לא נמצאו טפסים לזיכוי'
                    else:
                        if inventory.sign(r_f):
                            if 'phone' in r_f:
                                if r_f['phone']:
                                    msg = 'פיקוד העורף - גדוד ניוד\nהוחתמת על ציוד באופן דיגיטלי.\nלצפיה, יש להכנס בקישור המצורף:\n\n{}'.format(str(request.host_url))
                                    sms.send_sms(msg, [r_f['phone']])
                        return redirect('/close')
                if 'return' in r_v:
                    d_i = config.doc_items.copy()
                    d_i.append('to_ret')
                    return render_template('popup/return.html', data=data, doc_items=d_i, msg=msg,
                                           dictionary=config.dictionary)
                return render_template('popup/sign.html', descriptions=config.descriptions)
    return redirect('/')


@app.route('/inv', methods=['POST', 'GET'])
def inv():
    if 'username' in session:
        user = db_handle.validate_user(session['username'])
        if user:
            if user['department'] == config.admin_department:
                p_id = ''
                if 'p_id' in request.values:
                    p_id = request.values['p_id']
                all_inv = db_handle.all_inv(p_id)
                return render_template('inventory.html', inv=all_inv, dictionary=config.dictionary)
    return redirect('/')


@app.route('/get_info', methods=['POST', 'GET'])
def get_info():
    if 'username' in session:
        user = db_handle.validate_user(session['username'])
        if user:
            if user['department'] == config.admin_department:
                return db_handle.validate_user(request.values['id'])
    return {}


@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect('/')


@app.route('/init')
def init(force=False):
    if not force:
        if 'username' in session:
            user = db_handle.validate_user(session['username'])
            if user:
                if user['department'] != config.admin_department:
                    return
            else:
                return
    config.descriptions = db_handle.read_list('descriptions')
    config.dictionary = db_handle.read_list('dictionary')
    config.doc_items = db_handle.read_list('doc_items')
    config.user_items = db_handle.read_list('user_items')


if __name__ == '__main__':
    # Initialize
    init(True)
    # Run App
    app.secret_key = '!afD345eW%##$'
    app.run(host="0.0.0.0", port=config.server_port, debug=True)


