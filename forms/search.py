from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class SearchForm(FlaskForm):
    name = StringField("Имя")
    submit = SubmitField("Поиск")
