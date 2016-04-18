from flask import Flask
from flask_oauthlib.client import OAuth
from flask import session, redirect, request, url_for, jsonify
import requests
import json
import config

app = Flask(__name__)
app.secret_key = "development"

oauth = OAuth()

twitch = oauth.remote_app('twitch',
                          base_url='https://api.twitch.tv/kraken/',
                          request_token_url=None,
                          access_token_method='POST',
                          access_token_url='https://api.twitch.tv/kraken/oauth2/token',
                          authorize_url='https://api.twitch.tv/kraken/oauth2/authorize',
                          consumer_key=config.TWITCH_CLIENTID, # get at: https://www.twitch.tv/kraken/oauth2/clients/new
                          consumer_secret=config.TWITCH_SECRET,
                          request_token_params={'scope': ["user_read", "channel_check_subscription"]}
                          )


@app.route('/')
def index():
    if 'twitch_token' in session:
        # this works
        headers = {'Authorization': ("OAuth " + session['twitch_token'][0])}
        r = requests.get(twitch.base_url, headers=headers)
        return jsonify(json.loads(r.text))

        #this doesnt
        me = twitch.get("/")
        return jsonify(me.data)
    return redirect(url_for('login'))


@twitch.tokengetter
def get_twitch_token(token=None):
    return session.get('twitch_token')


@app.route('/login')
def login():
    return twitch.authorize(callback=url_for('authorized', _external=True))


@app.route('/login/authorized')
def authorized():
    resp = twitch.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error'],
            request.args['error_description']
        )
    session['twitch_token'] = (resp['access_token'], '')
    print(resp)
    me = twitch.get('/')
    return jsonify(me.data)


@app.route('/logout')
def logout():
    session.pop('twitch_token', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
