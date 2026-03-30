import datetime

import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from data.db_session import SqlAlchemyBase


class Messages(SqlAlchemyBase):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String)
    sender = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    data_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('chats.id'))
    chat = orm.relationship('Chats')
    sender_user = orm.relationship('User')