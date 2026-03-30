import datetime

import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

from data.db_session import SqlAlchemyBase


class Chats(SqlAlchemyBase):
    __tablename__ = 'chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user1 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user2 = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    time_change = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    messages = orm.relationship('Messages', back_populates='chat')
