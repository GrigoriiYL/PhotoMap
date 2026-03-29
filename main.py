from flask import Flask, render_template, request
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user_form import UserForm
from data.users import User

app = Flask(__name__)
with open('settings') as f:
    for line in f:
        app.config['SECRET_KEY'] = line

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    us = db_sess.get(User, id)
    db_sess.close()
    return us


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = UserForm()
    if form.validate_on_submit():

        if form.password.data != form.password_again.data:
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message='Пароли не совпадают')
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.email == form.email.data).all()
        if users:
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Пользователь с таким email уже существует")
        f = request.files['file']
        if f:
            f.save(f'static/prof_pic{form.email.data}_ava.jpg')
        db_sess = db_session.create_session()
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        if f:
            user.profile_photo_link = f'static/prof_pic{form.email.data}_ava.jpg'
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        return f"<img src=static/prof_pic{form.email.data}_ava.jpg height=100px width=100px>"
    return render_template('user_registration.html', title='Регистрация', form=form)


if __name__ == '__main__':
    db_session.global_init("db/PhotoMap.db")
    app.run(host='0.0.0.0', port=8080)
