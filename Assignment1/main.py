# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask, request, render_template, redirect, url_for

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
# app = Flask(__name__)

app = Flask(__name__, template_folder='template')

# @app.route('/')
# def hello():
#    """Return a friendly HTTP greeting."""
#    return 'Hello World!'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/text', methods=['GET', 'POST'])
def text(comments=[]):
    if request.method == "GET":
        return render_template('index.html', comments=comments)
    comments.append(request.form["text_input"])
    return redirect(url_for('text'))


# @app.route('/')
# def hello_world():
#    return 'Open the URL in another tab, and then go to /hello/yourname'


# @app.route('/hello/<name>')
# def hello_name(name):
#    return 'Hello ' + name + '!'


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]


# Reference: https://aryaboudaie.com/python/technical/educational/web/flask/2018/10/17/flask.html#how-to-get-user-input