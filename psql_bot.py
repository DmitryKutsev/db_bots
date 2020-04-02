import telebot
import time
# это хуйня для прокси на работе, надо будет удалить обязательно
from telebot import apihelper
import tinysegmenter # это сегментатор
import nltk
from datetime import datetime as dt
import json
import urllib
import psycopg2
import sys

conn = psycopg2.connect(dbname='token_bot', user='admen',
                        password='admen', host='127.0.0.1')
# elasticsearch-7.6.1$ sudo bin/elasticsearch-plugin install analysis-kuromoji
token = '1067161248:AAGVbyrOrub9c0duVrhOLnZLi0-4pOA3peg'

# это прокси на работе, тоже удалить обязательно
apihelper.proxy = {
  'http': 'socks5://user:p7imna9fpc@51.38.36.50:8080',
  'https': 'socks5://user:p7imna9fpc@51.38.36.50:8080'
}

tb = telebot.TeleBot(token)

# создает объект сегментатора для японского текста
segmenter = tinysegmenter.TinySegmenter()



def commands_func(upd):
    if len(upd) > 0:
        try:
            my_message = upd[-1].message
        except Exception as e:
            print("Atribute error check")
            print(e)
        # тут идет разбивка по языкам
        try:
            # здесь задается команда, на которую бот будет реагировать
            if my_message.text != 'NoneType' and '/tokenize_japanese@psql_tokenize_bot' in my_message.text.lower():
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = upd[-1].message.chat.id
                try:
                    # оттуда же берем отправителя(никнейм)
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                    print(my_sender)
                except Exception as e:
                    print(e)
                    # которого если нет, то будет анонимус
                    my_sender = 'anonymous'
                # оттуда же берется дата
                my_msg_full_date = upd[-1].message.date
                my_msg_datetime = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M")
                # потом надо вытащить то, что идет в сообщении после команды. разбиваем сообщение.
                my_msg_consists = upd[-1].message.text.split('/tokenize_japanese@psql_tokenize_bot')[1]
                # токенизатор
                my_tokenized_msg = ' | '.join(segmenter.tokenize(my_msg_consists))
                print(my_msg_datetime)
                # и все собирается в соответствующи маппингу словарь, потом отправляется в эластик
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender,  \
                               'msg_datetime': my_msg_datetime, 'msg': my_msg_consists, 'tokenized_msg': my_tokenized_msg}
                print(result_dict)
                insert_jpn_msg = """
                         INSERT INTO msg_japanese (msg_id, msg_time, sender, chat_id, msg, tokenized_msg) VALUES (%s, %s, %s, %s, %s, %s);
                 """
                cur = conn.cursor()
                print((upd[-1].message.message_id, my_msg_datetime, my_sender, my_chat_id,
                         my_msg_consists, my_tokenized_msg))
                cur.execute(insert_jpn_msg, (upd[-1].message.message_id, my_msg_datetime, my_sender, my_chat_id,
                         my_msg_consists, my_tokenized_msg))
                conn.commit()
                # и в телеграм сообщением
                tb.send_message(my_chat_id, 'Ваше сообщение обработано и записано в базу. ' + str(result_dict))
            elif my_message.text != 'NoneType' and '/show_all@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                select_jpn = """(SELECT * FROM msg_japanese)"""
                cur = conn.cursor()
                cur.execute(select_jpn)
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)
            elif my_message.text != 'NoneType' and '/show_user@psql_tokenize_bot' in my_message.text.lower():
                my_user = my_message.text.split('/show_user@psql_tokenize_bot')[1][1:]
                my_chat_id = upd[-1].message.chat.id
                select_jpn = """(SELECT * FROM msg_japanese WHERE sender = %s)"""
                cur = conn.cursor()
                cur.execute(select_jpn, [my_user])
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)
            elif my_message.text != 'NoneType' and '/show_by_date@psql_tokenize_bot' in my_message.text.lower():
                msg = my_message.text.split(' ')
                date_from = msg[1] + " " + msg[2] #2020-03-28 13:08:00
                date_to = msg[3] + " " + msg[4] #YYYY-MM-DD hh:mm:ss
                print(date_from)
                print(date_to)
                my_chat_id = upd[-1].message.chat.id
                select_jpn = """(SELECT * FROM msg_japanese WHERE msg_time between %s and %s)"""
                cur = conn.cursor()
                cur.execute(select_jpn, [date_from, date_to])
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)
            elif my_message.text != 'NoneType' and '/add_user@psql_tokenize_bot' in my_message.text.lower():
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = upd[-1].message.chat.id
                msg = my_message.text.split(' ')
                surename = ''
                if len(msg) > 4:
                    surename = msg[4]
                result_dict = {'nickname': msg[1], 'group_name': msg[2],  \
                                'name': msg[3] + " " + surename}
                print(result_dict)
                insert_jpn_msg = """
                         INSERT INTO users (nickname, group_name, name) VALUES (%s, %s, %s);
                 """
                cur = conn.cursor()
                cur.execute(insert_jpn_msg, (result_dict['nickname'], result_dict['group_name'], result_dict['name']))
                conn.commit()
                # и в телеграм сообщением
                tb.send_message(my_chat_id, 'Ваше сообщение обработано и записано в базу. ' + str(result_dict))
            elif my_message.text != 'NoneType' and '/registred_users@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                my_users = """(SELECT * FROM users)"""
                cur = conn.cursor()
                cur.execute(my_users)
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы зарегистрированных пользователей группы: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)
            elif my_message.text != 'NoneType' and '/add_bot@psql_tokenize_bot' in my_message.text.lower():
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = upd[-1].message.chat.id
                msg = my_message.text.split(' ')
                result_dict = {'botname': msg[1], 'user_name': msg[2]}
                print(result_dict)
                insert_jpn_msg = """
                         INSERT INTO bots (botname, server_user) VALUES ( %s, %s);
                 """
                cur = conn.cursor()
                cur.execute(insert_jpn_msg, (result_dict['botname'], result_dict['user_name']))
                conn.commit()
                tb.send_message(my_chat_id, 'Ваше сообщение обработано и записано в базу. ' + str(result_dict))
            elif my_message.text != 'NoneType' and '/registred_bots@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                my_bots= """(SELECT * FROM bots)"""
                cur = conn.cursor()
                cur.execute(my_bots)
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы зарегистрированных ботов группы: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)

            elif my_message.text != 'NoneType' and '/msgs_by_server_and_group@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                my_bots= """(SELECT * FROM msg_japanese WHERE sender IN (SELECT server_user from bots WHERE server_user in
                (SELECT nickname from users WHERE group_name = 'MKL-191')))"""
                cur = conn.cursor()
                cur.execute(my_bots)
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы сообщений зарегистрированных юзеров, ' +
                                            'состоящих в группе МКЛ-191 и держащих на сервере бота: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)
            elif my_message.text != 'NoneType' and '/users_and_bots@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                my_bots= """(SELECT botname, server_user, group_name, name
                 FROM bots LEFT JOIN users ON (bots.server_user = users.nickname))"""
                cur = conn.cursor()
                cur.execute(my_bots)
                result = cur.fetchall()
                tb.send_message(my_chat_id, 'Содержимое базы ботов, и зарегистрированных юзеров, ' +
                                            'держащих на сервере бота: \n ')
                for i in result:
                    print(i)
                    tb.send_message(my_chat_id, str(i))
                print(result)
            elif my_message.text != 'NoneType' and '/delete_user@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                msg = my_message.text.split(' ')
                result_dict = str(msg[1])
                print(result_dict)
                insert_jpn_msg = "DELETE FROM users WHERE nickname = %s"
                cur = conn.cursor()
                cur.execute(insert_jpn_msg, (result_dict, ))
                conn.commit()
                tb.send_message(my_chat_id, 'Удален юзер ' + str(result_dict))
            elif my_message.text != 'NoneType' and '/delete_bot@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                msg = my_message.text.split(' ')
                result_dict = str(msg[1])
                print(result_dict)
                insert_jpn_msg = "DELETE FROM bots WHERE botname = %s"
                cur = conn.cursor()
                cur.execute(insert_jpn_msg, (result_dict, ))
                conn.commit()
                # и в телеграм сообщением
                tb.send_message(my_chat_id, 'Удален бот ' + result_dict)
            elif my_message.text != 'NoneType' and '/info@psql_tokenize_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                msg = open("info.txt", "r", encoding="utf-8")
                result_dict = msg.read()
                tb.send_message(my_chat_id, result_dict)
        except Exception as e:
            print("main exception")
            print(e, sys.stdout)


# тут весь процесс телеграм-апи
def main():
    old_id = ''
    offset = None
    while False:
        time.sleep(5)
        try:
            # с каждым новым сообщением в телеграм-апи копится буфер этих сообщений(он хранит все, но в пределах какого-то окна)
            # чтобы оставаться в пределах окна, надо его пододвигать все время, это криво, но работает. Вот это оффсет
            offset = tb.get_updates()[-1].update_id
        except Exception as e:
            print(e)
            print("errors_offset")
    try:
        # смотрим, каким было последнее сообщение в чяте
        old_id = tb.get_updates(offset, 300, 15)[-1].message.message_id
        time.sleep(8)
    except Exception as e:
        print(e)
        print("get msg id error")

    while True:
        try:
            #  сдвиг оффсета
            if offset and offset <= tb.get_updates(offset, 300, 15)[-1].update_id:
                offset = tb.get_updates(offset, 300, 15)[-1].update_id + 1
        except Exception as e:
            print(e)
            print("offset error2", offset)
        try:
            # все последние принятые сообщения идут в переменную
            updates = tb.get_updates(offset, 300,15)
            time.sleep(4)
        except Exception as e:
            print(e)
            print("errors2")
        try:
            # и если это не предыдущее, значит пришло новое
            if updates[-1].message.message_id != old_id:
                # новое сообщение становится потом само предыдущим
                old_id = updates[-1].message.message_id
                try:
                    # а потом запускается функция высылки в чат и обработки сообщения, которая выше. туда передаются обновления телеги.
                    commands_func(updates)
                except Exception as e:
                    print(e)
                    print("errors3")
        except Exception as e:
            print(e)
            print("errors4")
# тут запуск основного цикла, чтобы он не запускался от импорта простого.
if __name__ == '__main__':
    main()