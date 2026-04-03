from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired


class BotCreateForm(FlaskForm):
    name = StringField("Наименование бота", validators=[DataRequired()])
    about = StringField("Описание бота", validators=[DataRequired()])
    submit = SubmitField("Создать")
