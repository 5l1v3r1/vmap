#!/usr/bin/env python3

import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    poem = flask.request.args.get('poem', 'harmonium')

    return flask.render_template('index.html', \
            poem=flask.Markup(open(poem, 'r').read().replace('\n', '<br>')))

app.run()
