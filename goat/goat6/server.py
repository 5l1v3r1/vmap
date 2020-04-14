#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)

poems = []

@app.route('/compose', methods=['POST'])
def compose():
    poems.append(flask.request.form.get('poem'))
    return flask.redirect('/')

@app.route('/')
def index():
    return flask.render_template('index.html', \
            poems=[flask.Markup(p) for p in poems])

app.run()
