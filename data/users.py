import datetime as dt
import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    profile_photo_link = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    subscribers = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=' ')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    orm.relationship('Messages', back_populates='sender_user')


    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password_test):
        return check_password_hash(self.hashed_password, password_test)
