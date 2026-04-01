from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired


class ChangeUserForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(max=35)])
    about = StringField("Расскажите о себе")
    submit = SubmitField("Изменить")
