import flask
import flask.ext.login as flask_login

app = flask.Flask(__name__)
app.secret_key = "hastag-donaspock"

"""
Flask-Login works via a login manager.
To kick things off, we'll set up the login manager by instantiating it and telling it about our Flask app:
"""
# Setup Flask-Login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

"""
To keep things simple we're going to use a dictionary to represent a database of users.
In a real application, this would be an actual persistence layer.
However it's important to point out this is a feature of Flask-Login: it doesn't care how your data is stored so long as you tell it how to retrieve it!

"""
# Our mock database.
users = {'foo@bar.tld': {'pw': 'secret'}}

"""
We also need to tell Flask-Login how to load a user from a Flask request and from its session.
To do this we need to define our user object, a user_loader callback, and a request_loader calledback.
"""
class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

"""
Now we're ready to define our views.
We can start with a login view, which will populate the session with authentication bits.
After that we can define a view that requires authentication.
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'></input>
                <input type='password' name='pw' id='pw' placeholder='password'></input>
                <input type='submit' name='submit'></input>
               </form>
               '''

    email = flask.request.form['email']
    if email in users and flask.request.form['pw'] == users[email]['pw']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return flask.redirect(flask.url_for('protected'))

    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

# Finally we can define a view to clear the session and log users out:
@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

"""
We now have a basic working application that makes use of session-based authentication.
To round things off, we should provide a callback for login failures:
"""
@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'

if __name__ == "__main__":
    app.run(debug=True)