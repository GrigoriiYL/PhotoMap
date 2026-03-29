from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired



class UserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повтор пароля", validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    about = StringField("Расскажите о себе")
    submit = SubmitField("Зарегистрироваться")