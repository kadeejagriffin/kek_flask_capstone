from app import db
import base64
import os
import re
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text

# User Model 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    token = db.Column(db.String(32), index = True, unique=True)
    token_expiration = db.Column(db.DateTime)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs.get('password', ''))

    def __repr__(self):
        return f"<User {self.id}|{self.username}>"
    
    def update(self,**kwargs):
        allowed_fields = {'first_name', 'last_name', 'email', 'username', 'password'}
        
        def camel_to_snake(string):
            return re.sub("([A-Z][A-Za-z]*)","_\1", string).lower()
        
        for key, value in kwargs.items():
            snake_key = camel_to_snake(key)
            if snake_key in allowed_fields:
                if snake_key == 'password':
                    self.set_password(value)
                else:
                    setattr(self, snake_key, value)
        self.save()

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)
        self.save()

    def check_password(self, plain_text_password):
        return check_password_hash(self.password, plain_text_password)

    def to_dict(self):
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "username": self.username,
            "email": self.email
        }
        
    def get_token(self):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode("utf-8") 
        self.token_expiration = now + timedelta(hours=1)
        self.save()
        return self.token
    
    
# Retreat Model
class Retreat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(50), nullable=True)  
    date = db.Column(db.Date, nullable=True)  
    cost = db.Column(db.String(20), nullable=True)  


    def __init__(self, name, location, description=None, duration=None, date=None, cost=None):
        self.name = name
        self.location = location
        self.description = description
        self.duration = duration
        self.date = date
        self.cost = cost
        
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'duration': self.duration,
            'cost': self.cost,
            'date': self.date
        }

# Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    retreat_id = db.Column(db.Integer, db.ForeignKey('retreat.id'), nullable=False)
