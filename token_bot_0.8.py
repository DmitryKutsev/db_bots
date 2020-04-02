import telebot
import time
# это хуйня для прокси на работе, надо будет удалить обязательно
from telebot import apihelper
import tinysegmenter # это сегментатор
import nltk
from datetime import datetime as dt
import json
import urllib
from elasticsearch import Elasticsearch

es=Elasticsearch()
# elasticsearch-7.6.1$ sudo bin/elasticsearch-plugin install analysis-kuromoji
token = '998097635:AAGMy_eEwgHaRIsIL7LxTgSLIs2K-u-SttY'

# это прокси на работе, тоже удалить обязательно
apihelper.proxy = {
  'http': 'socks5://user:p7imna9fpc@51.38.36.50:8080',
  'https': 'socks5://user:p7imna9fpc@51.38.36.50:8080'
}

tb = telebot.TeleBot(token)

# создает объект сегментатора для японской хуйни
segmenter = tinysegmenter.TinySegmenter()



# это функция, которая смотрит, че за сообщение, и в зависимости от его содержания,
# сортирует, а потом высылает ответ. На вход она принимает апдейт(последнее сообщение)
# из функции main
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
            if my_message.text != 'NoneType' and '/tokenize_japanese@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    # оттуда же берем отправителя(никнейм)
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    # которого если нет, то будет анонимус
                    my_sender = 'anonymous'
                # оттуда же берется дата, и разбивается на время, дату, и времядату
                my_msg_full_date = tb.get_updates()[-1].message.date
                my_msg_datetime = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M")
                my_msg_date = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M").split()[0]
                my_msg_time = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y:%m:%d %H:%M").split()[1]
                # потом надо вытащить то, что идет в сообщении после команды. разбиваем сообщение.
                my_msg_consists = tb.get_updates()[-1].message.text.split('/tokenize_japanese@tokenize_sent_bot')[1]
                # это ,собственно, токенизатор
                my_tokenized_msg = ' | '.join(segmenter.tokenize(my_msg_consists))
                print(my_msg_datetime)
                # и все собирается в соответствующи маппингу словарь, потом отправляется в эластик
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender, 'msg_time': my_msg_time, 'msg_date': my_msg_date, \
                               'msg_datetime': my_msg_datetime, 'msg': my_msg_consists, 'tokenized_msg': my_tokenized_msg}
                es.index(index="japanese", doc_type='msg', body=result_dict)
                # и в телеграм сообщением
                tb.send_message(my_chat_id, 'Ваше сообщение обработано и записано в базу. ' + str(result_dict))
            elif my_message.text != 'NoneType' and '/tokenize_russian@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    # оттуда же берем отправителя(никнейм)
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    # которого если нет, то будет анонимус
                    my_sender = 'anonymous'
                # оттуда же берется дата, и разбивается на время, дату, и времядату
                my_msg_full_date = tb.get_updates()[-1].message.date
                my_msg_datetime = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M")
                my_msg_date = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M").split()[0]
                my_msg_time = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y:%m:%d %H:%M").split()[1]
                # потом надо вытащить то, что идет в сообщении после команды. разбиваем сообщение.
                my_msg_consists = tb.get_updates()[-1].message.text.split('/tokenize_russian@tokenize_sent_bot ')[1]
                # это ,собственно, токенизатор
                my_tokenized_msg = my_msg_consists.split(' ')
                print(my_msg_datetime)
                # и все собирается в соответствующи маппингу словарь, потом отправляется в эластик
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender, 'msg_time': my_msg_time,
                               'msg_date': my_msg_date, 'msg_datetime': my_msg_datetime, 'msg': my_msg_consists,
                               'tokenized_msg': my_tokenized_msg}
                es.index(index="russian", doc_type='msg', body=result_dict)
                # и в телеграм сообщением
                tb.send_message(my_chat_id, 'Ваше сообщение обработано и записано в базу. ' + str(result_dict))

            elif my_message.text != 'NoneType' and '/tokenize_korean@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                # берем из апдейтов телеграма последнее сообщение, и из него чат-айди, чтобы
                # знать, куда отвечать, да и вообще.
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    # оттуда же берем отправителя(никнейм)
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    # которого если нет, то будет анонимус
                    my_sender = 'anonymous'
                # оттуда же берется дата, и разбивается на время, дату, и времядату
                my_msg_full_date = tb.get_updates()[-1].message.date
                my_msg_datetime = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M")
                my_msg_date = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y-%m-%d %H:%M").split()[0]
                my_msg_time = dt.utcfromtimestamp(my_msg_full_date).strftime("%Y:%m:%d %H:%M").split()[1]
                # потом надо вытащить то, что идет в сообщении после команды. разбиваем сообщение.
                my_msg_consists = tb.get_updates()[-1].message.text.split('/tokenize_korean@tokenize_sent_bot ')[1]
                # это ,собственно, токенизатор
                my_tokenized_msg = my_msg_consists.split(' ')
                print(my_msg_datetime)
                # и все собирается в соответствующи маппингу словарь, потом отправляется в эластик
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender, 'msg_time': my_msg_time,
                               'msg_date': my_msg_date, 'msg_datetime': my_msg_datetime, 'msg': my_msg_consists,
                               'tokenized_msg': my_tokenized_msg}
                es.index(index="korean", doc_type='msg', body=result_dict)
                # и в телеграм сообщением
                tb.send_message(my_chat_id, 'Ваше сообщение обработано и записано в базу. ' + str(result_dict))

###Инфо

            elif my_message.text != 'NoneType' and '/info@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = upd[-1].message.chat.id
                msg1 = open("info1.txt", "r", encoding="utf-8")
                msg2 = open("info2.txt", "r", encoding="utf-8")
                msg3 = open("info3.txt", "r", encoding="utf-8")
                msg4 = open("info4.txt", "r", encoding="utf-8")
                result_dict1 = msg1.read()
                result_dict2 = msg2.read()
                result_dict3 = msg3.read()
                result_dict4 = msg4.read()
                tb.send_message(my_chat_id, result_dict1)
                tb.send_message(my_chat_id, result_dict2)
                tb.send_message(my_chat_id, result_dict3)
                tb.send_message(my_chat_id, result_dict4)
### инфо

            elif my_message.text != 'NoneType' and '/show_query_japanese_user@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'

                my_msg_consists = tb.get_updates()[-1].message.text.split('/show_query_japanese_user@tokenize_sent_bot')[1]
                print(my_msg_consists)
                msgs = es.search(index="japanese_mess", body={"query": {"match": {"sender": my_msg_consists[1:]}}})
                for i in msgs['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди - '  + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))
            #ФИЛЬТР по времени(пока не тестил, но по идее должно работать.
            #TODO оттестить времяфильтр
            elif my_message.text != 'NoneType' and '/japanese_time_ranged@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                my_msg_consists = tb.get_updates()[-1].message.text.split()
                time_from = my_msg_consists[1]
                time_to = my_msg_consists[2]
                msgs = es.search(index="japanese", body={"query": {"range": {"msg_time":  {"gte": time_from, "lt": time_to}
                                                                             }}})
                print(msgs)
                tb.send_message(my_chat_id, msgs)
                for i in msgs['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_time_ranged@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                my_msg_consists = tb.get_updates()[-1].message.text.split()
                time_from = my_msg_consists[1]
                time_to = my_msg_consists[2]
                msgs = es.search(index="korean", body={"query": {"range": {"msg_time":  {"gte": time_from,
                                                                                         "lt": time_to}
                                                                             }}})
                print(msgs)
                tb.send_message(my_chat_id, msgs)
                for i in msgs['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))


            elif my_message.text != 'NoneType' and '/russian_time_ranged@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                my_msg_consists = tb.get_updates()[-1].message.text.split()
                time_from = my_msg_consists[1]
                time_to = my_msg_consists[2]
                msgs = es.search(index="russian", body={"query": {"range": {"msg_time":  {"gte": time_from,
                                                                                         "lt": time_to}
                                                                             }}})
                print(msgs)
                tb.send_message(my_chat_id, msgs)
                for i in msgs['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            # ФИЛЬТР по дате и времени, ловит сообщение с двумя метками дата+время через пробел
            elif my_message.text != 'NoneType' and '/korean_datetime_ranged@tokenize_sent_bot' in \
                    my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                # тут просто разбивается сообщение с временным интервалом,
                # из него склеиваются интервалы, соответствующие маппингу

                my_msg_consists = tb.get_updates()[-1].message.text.split()
                time_from = my_msg_consists[1] + " " + my_msg_consists[2]
                time_to = my_msg_consists[3] + " " + my_msg_consists[4]
                # и отправляется запрос с ними в эластик
                msgs = es.search(index="korean", body={"query": {"range": {"msg_datetime":  {"gte": time_from,
                                                                                         "lt": time_to}
                                                  }}})
                print(msgs)
                # потом это все разбирается, и отправляется в чат по кусочкам, для каждого
                # попавшего в диапазон фильтра значения
                tb.send_message(my_chat_id, msgs)
                for i in msgs['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/russian_datetime_ranged@tokenize_sent_bot' in \
                    my_message.text.lower():
                    result_dict = {}
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    try:
                        my_sender = tb.get_updates()[-1].message.json['from']['username']
                    except Exception as e:
                        print(e)
                        my_sender = 'anonymous'
                    # тут просто разбивается сообщение с временным интервалом,
                    # из него склеиваются интервалы, соответствующие маппингу

                    my_msg_consists = tb.get_updates()[-1].message.text.split()
                    time_from = my_msg_consists[1] + " " + my_msg_consists[2]
                    time_to = my_msg_consists[3] + " " + my_msg_consists[4]
                    # и отправляется запрос с ними в эластик
                    msgs = es.search(index="russian",
                                     body={"query": {"range": {"msg_datetime": {"gte": time_from, "lt": time_to}
                                                               }}})
                    print(msgs)
                    # потом это все разбирается, и отправляется в чат по кусочкам, для каждого
                    # попавшего в диапазон фильтра значения
                    tb.send_message(my_chat_id, msgs)
                    for i in msgs['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/japanese_datetime_ranged@tokenize_sent_bot' in my_message.text.lower():
                    result_dict = {}
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    try:
                        my_sender = tb.get_updates()[-1].message.json['from']['username']
                    except Exception as e:
                        print(e)
                        my_sender = 'anonymous'
                    # тут просто разбивается сообщение с временным интервалом,
                    # из него склеиваются интервалы, соответствующие маппингу

                    my_msg_consists = tb.get_updates()[-1].message.text.split()
                    time_from = my_msg_consists[1] + " " + my_msg_consists[2]
                    time_to = my_msg_consists[3] + " " + my_msg_consists[4]
                    # и отправляется запрос с ними в эластик
                    msgs = es.search(index="japanese",
                                     body={"query": {"range": {"msg_datetime": {"gte": time_from, "lt": time_to}
                                                               }}})
                    print(msgs)
                    # потом это все разбирается, и отправляется в чат по кусочкам, для каждого
                    # попавшего в диапазон фильтра значения
                    tb.send_message(my_chat_id, msgs)
                    for i in msgs['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_datetime_ranged@tokenize_sent_bot' in \
                    my_message.text.lower():
                    result_dict = {}
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    try:
                        my_sender = tb.get_updates()[-1].message.json['from']['username']
                    except Exception as e:
                        print(e)
                        my_sender = 'anonymous'
                    # тут просто разбивается сообщение с временным интервалом,
                    # из него склеиваются интервалы, соответствующие маппингу

                    my_msg_consists = tb.get_updates()[-1].message.text.split()
                    time_from = my_msg_consists[1] + " " + my_msg_consists[2]
                    time_to = my_msg_consists[3] + " " + my_msg_consists[4]
                    # и отправляется запрос с ними в эластик
                    msgs = es.search(index="korean",
                                     body={"query": {"range": {"msg_datetime": {"gte": time_from, "lt": time_to}
                                                               }}})
                    print(msgs)
                    # потом это все разбирается, и отправляется в чат по кусочкам, для каждого
                    # попавшего в диапазон фильтра значения
                    tb.send_message(my_chat_id, msgs)
                    for i in msgs['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/russian_datetime_ranged@tokenize_sent_bot' in \
                    my_message.text.lower():
                    result_dict = {}
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    try:
                        my_sender = tb.get_updates()[-1].message.json['from']['username']
                    except Exception as e:
                        print(e)
                        my_sender = 'anonymous'
                    # тут просто разбивается сообщение с временным интервалом,
                    # из него склеиваются интервалы, соответствующие маппингу

                    my_msg_consists = tb.get_updates()[-1].message.text.split()
                    time_from = my_msg_consists[1] + " " + my_msg_consists[2]
                    time_to = my_msg_consists[3] + " " + my_msg_consists[4]
                    # и отправляется запрос с ними в эластик
                    msgs = es.search(index="russian",
                                     body={"query": {"range": {"msg_datetime": {"gte": time_from, "lt": time_to}
                                                               }}})
                    print(msgs)
                    # потом это все разбирается, и отправляется в чат по кусочкам, для каждого
                    # попавшего в диапазон фильтра значения
                    tb.send_message(my_chat_id, msgs)
                    for i in msgs['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))


                    # Раздельный поиск, совместный поиск и удаление
                    # Японский
            elif my_message.text != 'NoneType' and '/japanese_search_name@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    sender_targ = tb.get_updates()[-1].message.text.split('/japanese_search_name@tokenize_sent_bot ')[1]
                    sender_msg = es.search(index="japanese", body={"query": {"match": {'sender': sender_targ}}})
                    print(sender_msg)
                    tb.send_message(my_chat_id, sender_msg)
                    for i in sender_msg['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/japanese_delete_name@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    sender_targ = tb.get_updates()[-1].message.text.split('/japanese_delete_name@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="japanese", body={"query": {"match": {"sender": sender_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')


            elif my_message.text != 'NoneType' and '/japanese_search_msg@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    msg_targ = tb.get_updates()[-1].message.text.split('/japanese_search_msg@tokenize_sent_bot ')[1]
                    msg_msg = es.search(index="japanese", body={"query": {"match": {'msg': msg_targ}}})
                    print(msg_msg)
                    tb.send_message(my_chat_id, msg_msg)
                    for i in msg_msg['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))


            elif my_message.text != 'NoneType' and '/japanese_delete_msg@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    msg_targ = tb.get_updates()[-1].message.text.split('/japanese_delete_msg@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="japanese", body={"query": {"match": {"msg": msg_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')


            elif my_message.text != 'NoneType' and '/japanese_search_token@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    msg_targ = tb.get_updates()[-1].message.text.split('/japanese_search_token@tokenize_sent_bot ')[1]
                    msg_msg_token = es.search(index='japanese', body={"query": {"match": {"tokenized_msg": msg_targ}}})
                    print(msg_msg_token)
                    tb.send_message(my_chat_id, msg_msg_token)
                    for i in msg_msg_token['hits']['hits']:
                        print(i)
                        tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                        tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                        tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                        tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                        tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))


            elif my_message.text != 'NoneType' and '/japanese_delete_token@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    msg_targ = tb.get_updates()[-1].message.text.split('/japanese_delete_token@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="japanese", body={"query": {"match": {"tokenized_msg": msg_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/japanese_search_date@tokenize_sent_bot' in \
                     my_message.text.lower():
                date_targ = tb.get_updates()[-1].message.text.split('/japanese_search_date@tokenize_sent_bot ')[1]
                print(date_targ)
                date_msg = es.search(index="japanese", body={"query": {"match": {'msg_date': date_targ}}})
                print(date_msg)
                tb.send_message(date_msg)
                for i in date_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/japanese_delete_date@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    date_targ = tb.get_updates()[-1].message.text.split('/japanese_delete_msg@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="japanese", body={"query": {"match": {"msg_date": date_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/japanese_search_time@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                time_targ = tb.get_updates()[-1].message.text.split('/japanese_search_time@tokenize_sent_bot ')[1]
                time_msg = es.search(index="japanese", body={"query": {"match": {'msg_time': time_targ}}})
                print(time_msg)
                tb.send_message(my_chat_id, time_msg)
                for i in time_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/japanese_delete_time@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    time_targ = tb.get_updates()[-1].message.text.split('/japanese_delete_time@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="japanese", body={"query": {"match": {"msg_time": msg_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')

            #Совместный поиск
            # по нику и дате
            elif my_message.text != 'NoneType' and '/japanese_search_name_and_date@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split(' ')[1]
                date_targ = tb.get_updates()[-1].message.text.split(' ')[2]
                query_msg = es.search(index="japanese", body={"query": {"bool": {"must":[{"match": {"sender":
                                                                                                            sender_targ}},
                                                                                             {"match": {"msg_date":
                                                                                                            date_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            #по нику и сообщению
            elif my_message.text != 'NoneType' and '/japanese_search_msg_and_name@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split(' ')[-1]
                print(sender_targ)
                msg_targ = tb.get_updates()[-1].message.text.split('/japanese_search_msg_and_name@tokenize_sent_bot ')[1]
                print(msg_targ)
                msg_targ = msg_targ.split(' ')[:-1]
                print(msg_targ)
                msg_targ = ' '.join(msg_targ)
                print(msg_targ)
                query_msg = es.search(index="japanese", body={"query": {"bool": {"must":[{"match": {"sender":
                                                                                                            sender_targ}},
                                                                                             {"match": {"msg":
                                                                                                            msg_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

                # по сообщению и дате
            elif my_message.text != 'NoneType' and '/japanese_search_msg_and_date@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split(' ')[-1]
                msg_targ = tb.get_updates()[-1].message.text.split('/japanese_search_msg_and_date@tokenize_sent_bot ')[1]
                print(msg_targ)
                msg_targ = msg_targ.split(' ')[:-1]
                print(msg_targ)
                msg_targ = ' '.join(msg_targ)
                query_msg = es.search(index="japanese", body={"query": {"bool": {"must": [{"match": {"msg_date":
                                                                                                                 date_targ}},
                                                                                                  {"match": {"msg":
                                                                                                                 msg_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            # Корейский
            elif my_message.text != 'NoneType' and '/korean_search_name@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split('/korean_search_name@tokenize_sent_bot ')[1]
                sender_msg = es.search(index="korean", body={"query": {"match": {'sender': sender_targ}}})
                print(sender_msg)
                tb.send_message(my_chat_id, sender_msg)
                for i in sender_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_delete_name@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    sender_targ = tb.get_updates()[-1].message.text.split('/korean_delete_name@tokenize_sent_bot')[1]
                    es.delete_by_query(index="korean", body={"query": {"match": {"sender": sender_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/korean_search_msg@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/korean_search_name@tokenize_sent_bot ')[1]
                msg_msg = es.search(index="korean", body={"query": {"match": {'msg': msg_targ}}})
                print(msg_msg)
                tb.send_message(my_chat_id, msg_msg)
                for i in msg_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_delete_msg@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/korean_delete_msg@tokenize_sent_bot ')[1]
                es.delete_by_query(index="korean", body={"query": {"match": {"msg": msg_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/korean_search_token@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/korean_search_token@tokenize_sent_bot ')[1]
                msg_msg_token = es.search(index="korean", body={"query": {"match": {"tokenized_msg": msg_targ}}})
                print(msg_msg_token)
                tb.send_message(my_chat_id, msg_msg_token)
                for i in msg_msg_token['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_delete_token@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/korean_delete_token@tokenize_sent_bot ')[1]
                es.delete_by_query(index="korean", body={"query": {"match": {"tokenized_msg": msg_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')


            elif my_message.text != 'NoneType' and '/korean_search_date@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split('/korean_search_date@tokenize_sent_bot ')[1]
                date_msg = es.search(index="korean", body={"query": {"match": {'msg_date': date_targ}}})
                print(date_msg)
                tb.send_message(my_chat_id, date_msg)
                for i in date_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_delete_date@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split('/korean_delete_date@tokenize_sent_bot ')[1]
                es.delete_by_query(index="korean", body={"query": {"match": {"msg_date": date_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/korean_search_time@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                time_targ = tb.get_updates()[-1].message.text.split('/korean_search_time@tokenize_sent_bot ')[1]
                time_msg = es.search(index="korean", body={"query": {"match": {'msg_time': time_targ}}})
                print(time_msg)
                tb.send_message(my_chat_id, time_msg)
                for i in time_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/korean_delete_time@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    time_targ = tb.get_updates()[-1].message.text.split('/korean_delete_time@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="korean", body={"query": {"match": {"msg_time": time_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')

            # Совместный поиск
            # по нику и дате
            elif my_message.text != 'NoneType' and '/korean_search_name_and_date@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split(' ')[1]
                date_targ = tb.get_updates()[-1].message.text.split(' ')[2]
                query_msg = es.search(index="korean", body={"query": {"bool": {"must": [{"match": {"sender":
                                                                                                             sender_targ}},
                                                                                              {"match": {"msg_date":
                                                                                                             date_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            # по нику и сообщению
            elif my_message.text != 'NoneType' and '/korean_search_msg_and_name@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split(' ')[-1]
                msg_targ = tb.get_updates()[-1].message.text.split('/korean_search_msg_and_name@tokenize_sent_bot ')[1]
                print(msg_targ)
                msg_targ = msg_targ.split(' ')[:-1]
                print(msg_targ)
                msg_targ = ' '.join(msg_targ)
                query_msg = es.search(index="korean", body={"query": {"bool": {"must": [{"match": {"sender":
                                                                                                         sender_targ}},
                                                                                          {"match": {"msg":
                                                                                                         msg_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

                # по сообщению и дате
            elif my_message.text != 'NoneType' and '/korean_search_msg_and_date@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split(' ')[-1]
                msg_targ = tb.get_updates()[-1].message.text.split('/korean_search_msg_and_date@tokenize_sent_bot ')[1]
                print(msg_targ)
                msg_targ = msg_targ.split(' ')[:-1]
                print(msg_targ)
                msg_targ = ' '.join(msg_targ)
                query_msg = es.search(index="korean", body={"query": {"bool": {"must": [{"match": {"msg_date":
                                                                                                         date_targ}},
                                                                                          {"match": {"msg":
                                                                                                         msg_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            # Русский
            elif my_message.text != 'NoneType' and '/russian_search_name@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split('/russian_search_name@tokenize_sent_bot ')[1]
                sender_msg = es.search(index="russian", body={"query": {"match": {'sender': sender_targ}}})
                print(sender_msg)
                tb.send_message(my_chat_id, sender_msg)
                for i in sender_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/russian_delete_name@tokenize_sent_bot' in \
                         my_message.text.lower():
                    my_chat_id = tb.get_updates()[-1].message.chat.id
                    sender_targ = tb.get_updates()[-1].message.text.split('/russian_delete_name@tokenize_sent_bot ')[1]
                    es.delete_by_query(index="russian", body={"query": {"match": {"sender": sender_targ}}})
                    tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/russian_search_msg@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/russian_search_msg@tokenize_sent_bot ')[1]
                #print(msg_targ)
                msg_msg_sent = es.search(index="russian", body={"query": {"match": {"msg": msg_targ}}})
                tb.send_message(my_chat_id, msg_msg_sent)
                print(msg_msg_sent)
                for i in msg_msg_sent['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/russian_delete_msg@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/russian_delete_msg@tokenize_sent_bot ')[1]
                es.delete_by_query(index="russian", body={"query": {"match": {"msg": msg_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/russian_search_token@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/russian_search_token@tokenize_sent_bot ')[1]
                msg_msg_token = es.search(index="russian", body={"query": {"match": {"tokenized_msg": msg_targ}}})
                print(msg_msg_token)
                tb.send_message(my_chat_id, msg_msg_token)
                for i in msg_msg_token['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            elif my_message.text != 'NoneType' and '/russian_delete_token@tokenize_sent_bot' in \
                         my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                msg_targ = tb.get_updates()[-1].message.text.split('/russian_delete_token@tokenize_sent_bot ')[1]
                es.delete_by_query(index="russian", body={"query": {"match": {"tokenized_msg": msg_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/russian_search_date@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split('/russian_search_date@tokenize_sent_bot ')[1]
                print(date_targ)
                date_msg = es.search(index="russian", body={"query": {"match": {'msg_date': date_targ}}})
                print(date_msg)
                tb.send_message(my_chat_id, date_msg)
                for i in date_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))


            elif my_message.text != 'NoneType' and '/russian_delete_date@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split('/russian_delete_date@tokenize_sent_bot ')[1]
                es.delete_by_query(index="russian", body={"query": {"match": {"msg_date": date_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')

            elif my_message.text != 'NoneType' and '/russian_search_time@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                time_targ = tb.get_updates()[-1].message.text.split('/russian_search_time@tokenize_sent_bot ')[1]
                time_msg = es.search(index="russian", body={"query": {"match": {'msg_time': time_targ}}})
                print(time_msg)
                tb.send_message(my_chat_id, time_msg)
                for i in time_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))


            elif my_message.text != 'NoneType' and '/russian_delete_time@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                time_targ = tb.get_updates()[-1].message.text.split('/russian_delete_time@tokenize_sent_bot ')[1]
                es.delete_by_query(index="russian", body={"query": {"match": {"msg_time": time_targ}}})
                tb.send_message(my_chat_id, 'Запись удалена')

            # Совместный поиск
            # по нику и дате
            elif my_message.text != 'NoneType' and '/russian_search_name_and_date@tokenize_sent_bot' in my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split(
                    ' ')[1]
                date_targ = tb.get_updates()[-1].message.text.split(
                    ' ')[2]
                query_msg = es.search(index="russian", body={"query": {"bool": {"must": [{"match": {"sender":
                                                                                                       sender_targ}},
                                                                                        {"match": {"msg_date":
                                                                                                       date_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

            # по нику и сообщению
            elif my_message.text != 'NoneType' and '/russian_search_msg_and_name@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                sender_targ = tb.get_updates()[-1].message.text.split(' ')[-1]
                msg_targ = tb.get_updates()[-1].message.text.split('/russian_search_msg_and_name@tokenize_sent_bot ')[1]
                print(msg_targ)
                msg_targ = msg_targ.split(' ')[:-1]
                print(msg_targ)
                msg_targ = ' '.join(msg_targ)
                query_msg = es.search(index="russian", body={"query": {"bool": {"must": [{"match": {"sender":
                                                                                                       sender_targ}},
                                                                                        {"match": {"msg":
                                                                                                       msg_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

                # по сообщению и дате
            elif my_message.text != 'NoneType' and '/russian_search_msg_and_date@tokenize_sent_bot' in \
                    my_message.text.lower():
                my_chat_id = tb.get_updates()[-1].message.chat.id
                date_targ = tb.get_updates()[-1].message.text.split(' ')[-1]
                print(date_targ)
                msg_targ = tb.get_updates()[-1].message.text.split('/russian_search_msg_and_date@tokenize_sent_bot ')[1]
                print(msg_targ)
                msg_targ = msg_targ.split(' ')[:-1]
                print(msg_targ)
                msg_targ = ' '.join(msg_targ)
                query_msg = es.search(index="russian", body={"query": {"bool": {"must": [{"match": {"msg_date":
                                                                                                       date_targ}},
                                                                                        {"match": {"msg":
                                                                                                       msg_targ}}]}}})
                print(query_msg)
                tb.send_message(my_chat_id, query_msg)
                for i in query_msg['hits']['hits']:
                    print(i)
                    tb.send_message(my_chat_id, 'чат айди- ' + str(i['_source']['chat_id']))
                    tb.send_message(my_chat_id, 'datetime - ' + str(i['_source']['msg_datetime']))
                    tb.send_message(my_chat_id, 'дата - ' + str(i['_source']['msg_date']))
                    tb.send_message(my_chat_id, 'предложение - ' + str(i['_source']['msg']))
                    tb.send_message(my_chat_id, 'токены - ' + str(i['_source']['tokenized_msg']))

        except Exception as e:
            print("Msg error check")
            print(e)



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