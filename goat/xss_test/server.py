#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)

@app.route('/ping')
def ping():
    res = flask.Response('pong')
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res

app.run(port=9999)
