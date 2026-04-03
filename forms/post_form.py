from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class PostForm(FlaskForm):
    address = StringField("Адрес")
    submit = SubmitField("Создать пост")
