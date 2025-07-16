# C:\Users\sptzk\Desktop\backend\models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UserLogin(db.Model):
    __tablename__ = 'user_login'
    user_id = db.Column(db.String, primary_key=True, unique=True)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.String, db.ForeignKey('user_login.user_id'), primary_key=True)
    name = db.Column(db.String, nullable=False)
    gender = db.Column(db.String(1), nullable=False)  # 'M' or 'F'
    birth = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String, nullable=False)
    address = db.Column(db.String)