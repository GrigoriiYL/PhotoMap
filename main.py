import datetime

from flask import Flask, render_template, request, redirect, url_for
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user_form import UserForm, UserLoginForm
from data.users import User
from forms.search import SearchForm
from data.chats import Chats
from data.messages import Messages
from forms.chat import ChatForm

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
        filetype = f.filename.split('.')[-1].lower()
        if f:
            if filetype == 'jpg' or filetype == 'png' or filetype == 'jpeg':
                f.save(f'static/prof_pic/{form.email.data}.jpg')
            else:
                return render_template('user_registration.html', title='Регистрация', form=form,
                                       message='Необходимо выбрать файл типа png/jpg/jpeg')
        db_sess = db_session.create_session()
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        if f:
            user.profile_photo_link = f'/static/prof_pic/{form.email.data}.jpg'
        user.about = form.about.data
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        db_sess.close()
        # return f"<img src=static/prof_pic{form.email.data}_ava.jpg height=100px width=100px>"
        return redirect('/login')
    return render_template('user_registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            db_sess.close()
            return redirect('/')
        db_sess.close()
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, title='Авторизация')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.name.like('%' + form.name.data + '%'))
        db_sess.close()
        return render_template('search.html', form=form, users=users)
    return render_template('search.html', form=form)


@app.route('/')
def main():
    return render_template('base.html')


@app.route('/subscribe/<int:id>')
def subscribe(id):
    db_sess = db_session.create_session()
    user = db_sess.get(User, id)
    user.subscribers = user.subscribers + str(current_user.id) + ' '
    db_sess.commit()
    db_sess.close()
    return redirect('/search')


@app.route('/chat_search/<int:id>')
def chat_search(id):
    db_sess = db_session.create_session()
    chat1 = db_sess.query(Chats).filter(Chats.user1 == current_user.id, Chats.user2 == id).first()
    if chat1:
        return redirect(f'/open_chat/{chat1.id}')
    else:
        chat2 = db_sess.query(Chats).filter(Chats.user1 == id, Chats.user2 == current_user.id).first()
        if chat2:
            return redirect(f'/open_chat/{chat2.id}')
        else:
            chat = Chats(
                user1=current_user.id,
                user2=id
            )
            db_sess.add(chat)
            db_sess.commit()
            ch = db_sess.query(Chats).filter(Chats.user1 == current_user.id, Chats.user2 == id).first()
            db_sess.close()
            return redirect(f'/open_chat/{ch.id}')


@app.route('/open_chat/<int:id>', methods=['GET', 'POST'])
def open_chat(id):
    db_sess = db_session.create_session()
    chat = db_sess.query(Chats).filter(Chats.id == id).first()
    form = ChatForm()
    if form.validate_on_submit():
        msg = Messages(
            content=form.content.data,
            sender=current_user.id,
            chat_id=id
        )
        form.content.data = ''
        db_sess.add(msg)
        chat.time_change = datetime.datetime.now()
        db_sess.commit()
        db_sess.close()
        return redirect(f'/open_chat/{id}')
    messages = db_sess.query(Messages).filter(Messages.chat == chat).all()[::-1]
    rnd = render_template('chat.html', form=form, messages=messages)
    db_sess.commit()
    db_sess.close()
    return rnd


@app.route('/all_chats')
def get_all_chats():
    db_sess = db_session.create_session()
    chats = db_sess.query(Chats).filter((Chats.user1 == current_user.id) | (Chats.user2 == current_user.id)).all()
    res_chat_sp = []
    for el in chats:
        sp = []
        sp.append(el)
        if current_user.id != el.user1:
            sp.append(db_sess.get(User, el.user1))
        else:
            sp.append(db_sess.get(User, el.user2))
        res_chat_sp.append(sp)
    print(res_chat_sp)
    return render_template("all_chats.html", chats=sorted(res_chat_sp, key=lambda x: x[0].time_change, reverse=True))



if __name__ == '__main__':
    db_session.global_init("db/PhotoMap.db")
    app.run(host='0.0.0.0', port=8080)
