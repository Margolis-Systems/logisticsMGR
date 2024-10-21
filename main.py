from flask import Flask, render_template, redirect, request, make_response, stream_with_context, Response, session
from src import config, db_handler, inventory


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
    return render_template('main.html', data=data, doc_items=config.doc_items, msg=msg, dictionary=config.dictionary)


@app.route('/close', methods=['GET'])
def close():
    return render_template('popup/close.html')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    r_v = request.values
    msg = ''
    data = {}
    if request.form:
        r_f = dict(request.form)
        if 'return' in r_v:
            inventory.ret(r_f)
            if 'id' in r_f:
                data = db_handle.validate_user(r_f['id'])
        else:
            inventory.sign(r_f)
            return redirect('/close')
    if 'return' in r_v:
        d_i = config.doc_items.copy()
        d_i.append('check')
        return render_template('popup/return.html', data=data, doc_items=d_i, msg=msg,
                               dictionary=config.dictionary)
    return render_template('popup/sign.html')


@app.route('/inv', methods=['POST', 'GET'])
def inv():
    return render_template('inventory.html')


@app.route('/get_info', methods=['POST', 'GET'])
def get_info():
    return db_handle.validate_user(request.values['id'])


if __name__ == '__main__':
    app.secret_key = 'afd345eh%##$'
    app.run(host="0.0.0.0", port=config.server_port, debug=True)


