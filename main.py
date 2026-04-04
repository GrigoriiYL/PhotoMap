import datetime
import pprint
import json
import random

import schedule
from random import choice

from requests import get

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response, request
from data import db_session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms.user_form import UserForm, UserLoginForm
from data.users import User
from forms.search import SearchForm
from data.chats import Chats
from data.messages import Messages
from forms.chat import ChatForm
from forms.post_form import PostForm
from data.posts import Posts
from forms.comments_form import CommentForm
from data.comments import Comments
from forms.change_user_form import ChangeUserForm
from forms.bot_create_form import BotCreateForm
from data.bots import Bots
from data.bot_messages import BotMessages
from data.bot_chats import BotChats
from data import bots_api

static_apikey = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

app = Flask(__name__)
with open('settings') as f:
    for line in f:
        app.config['SECRET_KEY'] = line

login_manager = LoginManager()
login_manager.init_app(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.route('/')
def main():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).all()[::-1]
    rend = render_template('main_posts.html', posts=posts, href='/subs', href_text='Подписки')
    db_sess.close()
    return rend


@app.route('/open_post/<int:id>', methods=['GET', 'POST'])
def open_post(id):
    form = CommentForm()
    db_sess = db_session.create_session()
    db_sess.get(Posts, id)
    if form.validate_on_submit():
        com = Comments()
        com.content = form.content.data
        com.user_id = current_user.id
        com.post_id = id
        db_sess.add(com)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/open_post/{id}')
    comments = db_sess.query(Comments).filter(Comments.post_id == id).all()
    post = db_sess.query(Posts).filter(Posts.id == id).first()
    rend = render_template('open_post.html', comments=comments, post=post, form=form)
    db_sess.close()
    return rend


@app.route('/open_map/<int:id>')
def open_map(id):
    db_sess = db_session.create_session()
    post = db_sess.get(Posts, id)
    rend = render_template('map.html', post=post)
    db_sess.close()
    return rend


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
            db_sess.close()
            return render_template('user_registration.html', title='Регистрация', form=form,
                                   message="Пользователь с таким email уже существует")
        f = request.files['file']
        filetype = f.filename.split('.')[-1].lower()
        if f:
            if filetype == 'jpg' or filetype == 'png' or filetype == 'jpeg':
                f.save(f'static/prof_pic/{form.email.data}.jpg')
            else:
                db_sess.close()
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
        db_sess.close()
        return redirect(f'/open_chat/{chat1.id}')
    else:
        chat2 = db_sess.query(Chats).filter(Chats.user1 == id, Chats.user2 == current_user.id).first()
        if chat2:
            db_sess.close()
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
    if current_user.id == chat.user1 or current_user.id == chat.user2:
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
    return redirect('/all_chats')


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
    db_sess.close()
    return render_template("all_chats.html", chats=sorted(res_chat_sp, key=lambda x: x[0].time_change, reverse=True))


@app.route('/profile')
def open_profile():
    db_sess = db_session.create_session()
    posts = db_sess.query(Posts).filter(Posts.user_id == current_user.id).all()[::-1]
    db_sess.close()
    return render_template('profile.html', posts=posts)


@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        f = request.files['file']
        if f:
            file_type = f.filename.split('.')[-1].lower()
            if file_type == 'jpg' or file_type == 'jpeg' or file_type == 'png':
                address = form.address.data
                post = Posts()
                post.user_id = current_user.id
                db_sess = db_session.create_session()
                db_sess.add(post)
                db_sess.commit()
                if address:
                    try:
                        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
                        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
                        geocoder_request = f'{server_address}apikey={api_key}&geocode={address}&format=json'
                        response = get(geocoder_request).json()
                        # pprint.pprint(response)
                        # with open(f'{address}.json', 'w', encoding='utf8') as f:
                        #     js = json.dumps(response, indent=4, ensure_ascii=False)
                        #     print(js, file=f)
                        coords = response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point'][
                            'pos']
                        server_address = 'https://static-maps.yandex.ru/v1?'
                        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
                        ll_spn = f'll={','.join(coords.split())}&spn=0.020457,0.00619'

                        map_request = f"{server_address}{ll_spn}&apikey={api_key}"
                        response = get(map_request)
                        # print(response.url)
                        with open(f'static/maps/map{post.id}.png', "wb") as file:
                            file.write(response.content)

                        post.map_link = f'/static/maps/map{post.id}.png'
                    except Exception:
                        post.map_link = None

                f.save(f'static/posts/post{post.id}.jpg')
                post.img_link = f'/static/posts/post{post.id}.jpg'
                db_sess.commit()
                db_sess.close()
                return redirect('/')
            else:

                return render_template('post.html', form=form, message="Только форматы jpg, jpeg, json")

        else:
            return render_template('post.html', form=form, message="Выберите изображение")

    return render_template('post.html', form=form)


@app.route('/change_user/<int:id>', methods=['GET', 'POST'])
def change_user(id):
    form = ChangeUserForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.get(User, id)
        user.name = form.name.data
        user.about = form.about.data
        f = request.files['file']
        filetype = f.filename.split('.')[-1].lower()
        if f:
            if filetype == 'jpg' or filetype == 'png' or filetype == 'jpeg':
                f.save(f'static/prof_pic/{current_user.email}.jpg')
            else:
                db_sess.close()
                return render_template('user_change.html', title='Изменение профиля', form=form,
                                       message='Необходимо выбрать файл типа png/jpg/jpeg')
            user.profile_photo_link = f'/static/prof_pic/{current_user.email}.jpg'
        db_sess.commit()
        db_sess.close()
        return redirect('/profile')
    db_sess = db_session.create_session()
    user = db_sess.get(User, id)
    form.name.data = user.name
    form.about.data = user.about
    db_sess.close()
    return render_template('user_change.html', form=form)


@app.route('/subs')
def subs():
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.subscribers.like('% ' + str(current_user.id) + ' %')).all()
    sub_sp = [el.id for el in users]
    posts = db_sess.query(Posts).filter(Posts.user_id.in_(sub_sp)).all()[::-1]
    rend = render_template('main_posts.html', href='/', posts=posts, href_text='Все посты', title='Подписки')
    db_sess.close()
    return rend


@app.route('/create_bot', methods=['GET', 'POST'])
def create_bot():
    form = BotCreateForm()
    if form.validate_on_submit():
        alph = 'qwertyuiopasdfghj<>mn---::::zxcvbnm12345678900987654321QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuiopasdfghj<>mn---::::zxcvbnm12345678900987654321QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuiopasdfghj<><><>mn---::::zzxcvbnm12345678900987654321QWERTYUIOPLKJHGFDSAZXCVBNMqwertyuiopasdfghj<>mn---::::zxcvbnm12345678900987654321QWERTYUIOPLKJHGFDSAZXCVBNM'
        db_sess = db_session.create_session()
        all_api = [el.api_key for el in db_sess.query(Bots).all()]
        api_key = ''.join(random.choices(alph, k=35))
        while api_key in all_api:
            api_key = ''.join(random.choices(alph, k=35))
        bot = Bots()
        bot.api_key = api_key
        bot.name = form.name.data
        bot.user_id = current_user.id
        f = request.files['file']
        filetype = f.filename.split('.')[-1].lower()
        bot.about = form.about.data
        if f:
            if filetype == 'jpg' or filetype == 'png' or filetype == 'jpeg':
                db_sess.add(bot)
                db_sess.commit()
                f.save(f'static/bots_profile_photo/{bot.id}.jpg')
                bot.profile_photo_link = f'/static/bots_profile_photo/{bot.id}.jpg'
                db_sess.commit()
            else:
                db_sess.close()
                return render_template('bot_create.html', title='Создание бота', form=form,
                                       message='Необходимо выбрать файл типа png/jpg/jpeg')

        db_sess.add(bot)
        db_sess.commit()
        db_sess.close()
        return render_template('api.html', api_key=api_key)
    return render_template('bot_create.html', form=form, title='Создание бота')


@app.route('/all_bot_chat')
def get_all_bot_chats():
    db_sess = db_session.create_session()
    chats = db_sess.query(BotChats).filter(BotChats.user_id == current_user.id).all()
    rnd = render_template("all_bot_chats.html", chats=sorted(chats, key=lambda x: x.time_change, reverse=True))
    db_sess.close()
    return rnd


@app.route('/open_bot_chat/<int:id>', methods=['GET', 'POST'])
def open_bot_chat(id):
    db_sess = db_session.create_session()
    chat = db_sess.query(BotChats).filter(BotChats.id == id).first()
    if current_user.id == chat.user_id:
        form = ChatForm()
        if form.validate_on_submit():
            msg = BotMessages(
                content=form.content.data,
                bot_id=chat.bot_id,
                user_id=current_user.id,
                from_user=True,
                chat_id=id,
                user_name=current_user.name
            )
            form.content.data = ''
            db_sess.add(msg)
            chat.time_change = datetime.datetime.now()
            db_sess.commit()
            db_sess.close()
            return redirect(f'/open_bot_chat/{id}')
        messages = db_sess.query(BotMessages).filter(BotMessages.chat == chat).all()[::-1]
        rnd = render_template('bot_chat.html', form=form, messages=messages)
        db_sess.commit()
        db_sess.close()
        return rnd
    return redirect('/all_chats')


@app.route('/search_bots', methods=['GET', 'POST'])
def search_bots():
    form = SearchForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        bots = db_sess.query(Bots).filter(Bots.name.like('%' + form.name.data + '%'))
        db_sess.close()
        return render_template('search_bots.html', form=form, bots=bots)
    return render_template('search_bots.html', form=form)


@app.route('/bot_chat_search/<int:id>')
def bot_chat_search(id):
    db_ses = db_session.create_session()
    chat = db_ses.query(BotChats).filter(BotChats.bot_id == id, BotChats.user_id == current_user.id).first()
    if chat:
        db_ses.close()
        return redirect(f'/open_bot_chat/{chat.id}')
    else:
        chat = BotChats(
            bot_id=id,
            user_id=current_user.id
        )
        db_ses.add(chat)
        db_ses.commit()
        ch = db_ses.query(BotChats).filter(BotChats.bot_id == id, BotChats.user_id == current_user.id).first()
        db_ses.close()
        return redirect(f'/open_bot_chat/{ch.id}')


db_session.global_init("db/PhotoMap.db")
app.register_blueprint(bots_api.blueprint)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
