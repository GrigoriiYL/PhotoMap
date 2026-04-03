import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase


class Bots(SqlAlchemyBase):
    __tablename__ = 'bots'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.Integer)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    api_key = sqlalchemy.Column(sqlalchemy.Integer)
    profile_photo_link = sqlalchemy.Column(sqlalchemy.String, default='/static/bots_profile_photo/default_photo.png')
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    messages = orm.relationship('BotMessages', back_populates='bot')
    chats = orm.relationship('BotChats', back_populates='bot')
