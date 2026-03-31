from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired


class UserForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    password_again = PasswordField("Повтор пароля", validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired(), Length(max=35)])
    about = StringField("Расскажите о себе")
    submit = SubmitField("Зарегистрироваться")


class UserLoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Пароль")
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")
