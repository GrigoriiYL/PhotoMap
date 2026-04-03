import datetime

import sqlalchemy
import sqlalchemy.orm as orm

from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin



class BotChats(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'bot_chats'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    bot_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('bots.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    time_change = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)

    bot_messages = orm.relationship('BotMessages', back_populates='chat')
    bot = orm.relationship('Bots')
    user = orm.relationship('User')
