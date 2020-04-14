#!/usr/bin/env python3

import flask, psycopg2

conn = psycopg2.connect('dbname=test-sec user=nick')
cur = conn.cursor()

app = flask.Flask(__name__)

# Must be safe!
def filter(query):
    return query.replace('select', '').replace('union', '').replace('from', '')

def check_login(username, password):
    global conn, cur

    # This one has an unsafe login form
    try:
        cur.execute('select username from users where username = \'' + filter(username) + '\' and password = \'' + filter(password) + '\'')
    except Exception as e:
        cur.close()
        conn.close()

        conn = psycopg2.connect('dbname=test-sec user=nick')
        cur = conn.cursor()
        raise e
    return cur.fetchone()

def product_search(name):
    global conn, cur

    # But a safe query
    try:
        cur.execute('select name, description, price from products where name like %s', ('%' + name + '%', ))
    except Exception as e:
        cur.close()
        conn.close()

        conn = psycopg2.connect('dbname=test-sec user=nick')
        cur = conn.cursor()
        raise e
    return cur.fetchall()

@app.route('/login', methods=['POST'])
def login():
    if 'username' not in flask.request.form or 'password' not in flask.request.form:
        return flask.abort(400)
    else:
        result = check_login(flask.request.form['username'], flask.request.form['password'])
        response = flask.make_response(flask.redirect('/'))
        if result is not None:
            response.set_cookie('user', result[0])
        return response

@app.route('/')
def index():
    return flask.render_template('index.html', \
            products=product_search(flask.request.args.get('q', '')), \
            username=flask.request.cookies.get('user', ''))

app.run()
