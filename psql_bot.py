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
        # print(upd[-1].message.text)
        try:
            # вот тут как раз полное сообщение. в нем и чят айди, и время высылки содержится, и все остальное.
            # нам, наверное будет надо еще добавить время высылки и чят, но это не сложно, там посмотрим.
            my_message = upd[-1].message

        except Exception as e:
            print("Atribute error check")
            print(e)
        # тут идет разбивка по языкам
        try:
            # здесь задается команда, на которую бот будет реагировать
            if my_message.text != 'NoneType' and '/tokenize_japanese@psql_tokenize_bot' in my_message.text.lower():
                result_dict = {}
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = upd[-1].message.chat.id
                try:
                    # оттуда же берем отправителя(никнейм)
                    my_sender = upd.message.json['from']['username']
                except Exception as e:
                    print(e)
                    # которого если нет, то будет анонимус
                    my_sender = 'anonymous'
                # оттуда же берется дата, и разбивается на время, дату, и времядату
                my_msg_full_date = upd[-1].message.date
                my_msg_datetime = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M")
                # my_msg_date = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M").split()[0]
                # my_msg_time = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y:%m:%d %H:%M").split()[1]
                # потом надо вытащить то, что идет в сообщении после команды. разбиваем сообщение.
                my_msg_consists = upd[-1].message.text.split('/tokenize_japanese@psql_tokenize_bot')[1]
                # это ,собственно, токенизатор

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
                # create table one by one
                print((upd[-1].message.message_id, my_msg_datetime, my_sender, my_chat_id,
                         my_msg_consists, my_tokenized_msg))
                cur.execute(insert_jpn_msg, (upd[-1].message.message_id, my_msg_datetime, my_sender, my_chat_id,
                         my_msg_consists, my_tokenized_msg))
                #result = cur.fetchall()
                # close communication with the PostgreSQL database server
                #print(result)
                # commit the changes
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
            # чтобы оставаться в пределах окна, надо его пододвигать все время, это криво, но вроде работает вот это оффсет
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
            # все последние принятые сообщения идут в переменную апдейтс
            updates = tb.get_updates(offset, 300,15)
            time.sleep(4)
            #print(updates)
        except Exception as e:
            print(e)
            print("errors2")
        try:
            # и если это не предыдущее, значит пришло новое
            if updates[-1].message.message_id != old_id:
                #print(len(updates))
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