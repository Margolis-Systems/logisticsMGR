from flask import Flask, render_template, redirect, request, make_response, stream_with_context, Response, session
from src import config, db_handler, inventory, sms_handler

sms = sms_handler.Sms()
db_handle = db_handler.Mongo()
app = Flask('Logistics')


@app.route('/', methods=['POST', 'GET'])
def main_page():
    data = {}
    msg = ''
    if request.form:
        user = db_handle.validate_user(request.form['id'])
        if user:
            data = user
        else:
            msg = 'לא נמצאו תוצאות'
    # todo:
    # else:
    #     user = get_cookie
    #     if user:
    #         data = db_handle.validate_user(request.form['id'])
    return render_template('main.html', data=data, doc_items=config.doc_items, msg=msg, dictionary=config.dictionary)


@app.route('/close', methods=['GET'])
def close():
    return render_template('popup/close.html')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    # if not get_cookie:
    #     return redirect('/')
    r_v = request.values
    msg = ''
    data = {}
    if request.form:
        r_f = dict(request.form)
        if 'return' in r_v:
            inventory.ret(r_f)
            if 'id' in r_f:
                data = db_handle.validate_user(r_f['id'])
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


@app.route('/inv', methods=['POST', 'GET'])
def inv():
    p_id = ''
    # if not get_cookie:
    #     return redirect('/')
    if 'p_id' in request.values:
        p_id = request.values['p_id']
    all_inv = db_handle.all_inv(p_id)
    return render_template('inventory.html', inv=all_inv, dictionary=config.dictionary)


@app.route('/get_info', methods=['POST', 'GET'])
def get_info():
    # if not get_cookie:
    #     return redirect('/')
    return db_handle.validate_user(request.values['id'])


if __name__ == '__main__':
    temp = db_handle.read_list('descriptions')
    if temp:
        config.descriptions = temp['list']
    app.secret_key = '!afD345eW%##$'
    app.run(host="0.0.0.0", port=config.server_port, debug=True)


