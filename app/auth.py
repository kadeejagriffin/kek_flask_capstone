from app.models import User
from app import db
from datetime import datetime
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth


basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = db.session.execute(db.select(User).where(User.username == username)).scalar_one_or_none()
    if user is not None and user.check_password(password):
        return user
    return None

@basic_auth.error_handler
def handle_error(status):
    return {'error': "Incorrect username/password, please try again!"}, status

@token_auth.verify_token
def verify_token(token):
    user = db.session.execute(db.select(User).where(User.token == token)).scalar_one_or_none()
    if user is not None and user.token_expiration > datetime.utcnow():
        return user
    return None 

@token_auth.error_handler
def handle_error(status):
    return {'error': 'Incorrect token, please try again'}, status




