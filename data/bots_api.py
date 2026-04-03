from flask import jsonify, make_response, request, Blueprint
from .bot_chats import BotChats
from .bot_messages import BotMessages
from .bots import Bots
from . import db_session
import datetime as dt

blueprint = Blueprint(
    'bots_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/bots_api/all_chats')
def get_chats():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    if not 'api_key' in request.json:
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    messages = db_sess.query(BotMessages).filter(BotMessages.from_user == True,

                                                 BotMessages.api_usage == False).all()
    for el in messages:
        print(el.content)
        el.api_usage = True
    db_sess.commit()
    js = jsonify(
        {
            'messages':
                [item.to_dict(only=('content', 'user_id', 'user_name')) for item in messages]
        }
    )
    db_sess.close()
    return js


@blueprint.route('/bots_api/send_message', methods=['POST'])
def send_message():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in ['content', 'user_id', 'api_key']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    bot = db_sess.query(Bots).filter(Bots.api_key == request.json['api_key']).all()
    if not bot:
        db_sess.close()
        return make_response(jsonify({'error': 'Bad Api_key'}), 400)

    chat = db_sess.query(BotChats).filter(BotChats.user_id == request.json['user_id']).first()
    if not chat:
        db_sess.close()
        return make_response(jsonify({'error': 'This user is not using your bot'}), 400)

    mes = BotMessages()
    mes.content = request.json['content']
    mes.chat_id = chat.id
    mes.bot_id = chat.bot.id
    mes.user_id = request.json['user_id']
    db_sess.add(mes)
    db_sess.commit()
    db_sess.close()
    return jsonify({'Message sent': True})
