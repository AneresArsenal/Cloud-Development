import flask
import requests
import json
import os
from flask import request, render_template


CLIENT_ID = '900520642147-08sn9nssm5cc2rr6r8u6ha3tin8bb82u.apps.googleusercontent.com'
CLIENT_SECRET = 'R3ZOMBNjh_QLBNQs1_uUO9S5'
SCOPE = 'profile email'
REDIRECT_URI = 'https://hw6-tays-oauth.appspot.com/oauth2callback'

app = flask.Flask(__name__, template_folder='template')
app.secret_key = os.urandom(24)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        return render_template('index.html')
    else:
        return flask.redirect(flask.url_for('oauth2callback'))


@app.route('/result', methods=['GET', 'POST'])
def result():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = json.loads(flask.session['credentials'])
    if credentials['expires_in'] <= 0:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        state = request.args['state']
        headers = {'Authorization': 'Bearer {}'.format(credentials['access_token'])}
        req_uri = 'https://people.googleapis.com/v1/people/me?personFields=names,emailAddresses'
        result = requests.get(req_uri, headers=headers)
        json_result = result.json()
        first_name = json_result['names'][0]["givenName"]
        last_name = json_result['names'][0]["familyName"]
        return render_template('result.html', first_name=first_name, last_name=last_name, state=state)


@app.route('/oauth2callback')
def oauth2callback():
    if 'code' not in flask.request.args:
        auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code''&client_id={}&redirect_uri={}&scope={}').format(CLIENT_ID, REDIRECT_URI, SCOPE)
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        state = flask.request.args.get('session_state')
        data = {'code': auth_code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'}
        response = requests.post('https://oauth2.googleapis.com/token', data=data)
        flask.session['credentials'] = response.text
        return flask.redirect(flask.url_for('result', state=state))


if __name__ == '__main__':
    app.debug = False
    app.run()

# References:
# https://stackoverflow.com/questions/12096522/render-template-with-multiple-variables
# https://stackoverflow.com/questions/35657821/the-session-is-unavailable-because-no-secret-key-was-set-set-the-secret-key-on
# https://stackoverflow.com/questions/35291021/typeerror-the-json-object-must-be-str-not-response-with-python-3-4
# https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments
