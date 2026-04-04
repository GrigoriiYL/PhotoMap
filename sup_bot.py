import datetime
import pprint
import sqlite3
import schedule
from requests import get, post

con = sqlite3.connect('db/BD_sup.db')

cur = con.cursor()
in_work = None


def get_messages():
    global in_work
    print('-----------------------')
    api_key = 'KVJ6YX5Ug<>nfw>Fmy26eRbef<u2o:Wmp--'
    response = get('https://n0c9ku-2a03-d000-a4-39e2-20fe-65d1-6d84-3872.ru.tuna.am/bots_api/all_chats', json={
        'api_key': api_key
    }).json()['messages']

    for message in response:
        if message['user_id'] == 1:
            if in_work:
                response_post = post('https://n0c9ku-2a03-d000-a4-39e2-20fe-65d1-6d84-3872.ru.tuna.am/bots_api/send_message', json={
                    'content': message['content'],
                    'user_id': in_work[1],
                    'api_key': api_key
                }).json()
                pprint.pprint(response_post)
                cur.execute(f"""
                DELETE FROM queue
                WHERE id = {in_work[0]}
                """)
                con.commit()
                in_work = None

                all_on_bd = cur.execute("""SELECT * FROM queue""").fetchall()
                for el in all_on_bd:
                    print(el)
                if all_on_bd:
                    in_work = all_on_bd[0]
                    print(in_work)
                    response_post = post('https://n0c9ku-2a03-d000-a4-39e2-20fe-65d1-6d84-3872.ru.tuna.am/bots_api/send_message', json={
                        'content': in_work[3],
                        'user_id': 1,
                        'api_key': api_key
                    }).json()
                    pprint.pprint(response_post)
            else:
                response_post = post('https://n0c9ku-2a03-d000-a4-39e2-20fe-65d1-6d84-3872.ru.tuna.am/bots_api/send_message', json={
                    'content': 'Новых сообщений нет',
                    'user_id': 1,
                    'api_key': api_key
                }).json()
                pprint.pprint(response_post)

        else:
            cur.execute(f"""
            INSERT INTO queue(user_id, user_name, content) VALUES({message['user_id']}, '{message['user_name']}', '{message['content']}')
            """)
            con.commit()

            if in_work is None:
                all_on_bd = cur.execute("""SELECT * FROM queue""").fetchall()
                if all_on_bd:
                    in_work = all_on_bd[0]
                    response_post = post('https://n0c9ku-2a03-d000-a4-39e2-20fe-65d1-6d84-3872.ru.tuna.am/bots_api/send_message', json={
                        'content': in_work[3],
                        'user_id': 1,
                        'api_key': api_key
                    }).json()
                    pprint.pprint(response_post)



schedule.every(5).seconds.do(get_messages)

while True:
    schedule.run_pending()
