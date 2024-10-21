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
    if request.form:
        r_f = dict(request.form)
        if 'return' in r_v:
            inventory.ret(r_f)
        else:
            inventory.sign(r_f)
        return redirect('/close')
    if 'return' in r_v:
        return render_template('popup/return.html')
    return render_template('popup/sign.html')


@app.route('/inv', methods=['POST', 'GET'])
def inv():
    return render_template('inventory.html')


if __name__ == '__main__':
    app.secret_key = 'afd345eh%##$'
    app.run(host="0.0.0.0", port=config.server_port, debug=True)


