import datetime
from email.policy import default

import sqlalchemy
import sqlalchemy.orm as orm
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class BotMessages(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'bot_messages'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('bot_chats.id'))
    bot_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('bots.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    from_user = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    data_time = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    api_usage = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    bot = orm.relationship('Bots')
    chat = orm.relationship('BotChats')
    user = orm.relationship('User')
