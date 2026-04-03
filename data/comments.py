import datetime as dt
import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"))
    send_time = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.now())

    user = orm.relationship("User")
    post = orm.relationship('Posts')
