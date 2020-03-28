import telebot
import time
# это хуйня для прокси на работе, надо будет удалить обязательно
from telebot import apihelper
import tinysegmenter # это сегментатор
import nltk
import daytime
import json
import urllib

token = '998097635:AAGMy_eEwgHaRIsIL7LxTgSLIs2K-u-SttY'

#это прокси на работе, тоже удалить обязательно
apihelper.proxy = {
  'http': 'socks5://user:p7imna9fpc@51.38.36.50:8080',
  'https': 'socks5://user:p7imna9fpc@51.38.36.50:8080'
}

tb = telebot.TeleBot(token)

# создает объект сегментатора для японской хуйни
segmenter = tinysegmenter.TinySegmenter()

#переводчик
def dict_mult_symbol(inp_kanji):
    print(inp_kanji)
    url = 'https://kanjiapi.dev/v1/words/'
    kanji = urllib.parse.quote(inp_kanji[0])
    full_url = url + kanji
    try:
        data = urllib.request.urlopen(full_url).read()
    except urllib.error.HTTPError:
        result_string = "KANJI NOT FOUND"
        print(result_string)
        result_list = [result_string, result_string]
        return result_list
    result = json.loads(data)
    result_pron_string = ''
    result_trancl_string = ''
    result_list = []
    result_string = ''
    translations_string = ''
    for i in result:
        for j in i['variants']:
            if j['written'] and j['written'] == inp_kanji:
                pron = '\nPRONOUNCING: ' + str(j['pronounced'])
                result_pron_string = result_pron_string +  ', ' + str(j['pronounced'])
                result_trancl_string = result_trancl_string + ', ' + str(i['meanings'][0]['glosses'])[1:-1]
                print(i['meanings'][0]['glosses'])
                for translates in i['meanings'][0]['glosses']:
                    translations_string = translations_string + translates + ', '
                result_string = result_string + pron + "\nTRANSLATION: " + translations_string[0:-2]
                result_list = [result_pron_string[1:], result_trancl_string[2:-1] + '\'.']
    if len(result_trancl_string) > 1:
        print(result_pron_string)
        return result_list
    else:
        result_string = "KANJI NOT FOUND"
        result_list = [result_string, result_string]
        return result_list

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
            if my_message.text != 'NoneType' and '/tokenize_japanese@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                my_msg_date = time.ctime(tb.get_updates()[-1].message.date)
                my_msg_consists = tb.get_updates()[-1].message.text.split('/tokenize_japanese@tokenize_sent_bot')[1]
                my_tokenized_msg = ' | '.join(segmenter.tokenize(my_msg_consists))
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender, 'msg_date': my_msg_date, 'msg': my_msg_consists, 'tokenized_msg': my_tokenized_msg}
                # эта хуйня высылает сообщения в каждом операторе по идее, его и можно потом в базу пихать
                tb.send_message(my_chat_id, 'мудак. сукапетух ' + str(result_dict))
            elif my_message.text != 'NoneType' and '/tokenize_russian@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                my_msg_date = time.ctime(tb.get_updates()[-1].message.date)
                my_msg_consists = tb.get_updates()[-1].message.text.split('/tokenize_russian@tokenize_sent_bot')[1]
                my_tokenized_msg = my_msg_consists.lower().split()
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender, 'msg_date': my_msg_date, 'msg': my_msg_consists, 'tokenized_msg': my_tokenized_msg}
                tb.send_message(my_chat_id, 'мудак. сукапетух ' + "\n" + str(result_dict))
            elif my_message.text != 'NoneType' and '/tokenize_korean@tokenize_sent_bot' in my_message.text.lower():
                result_dict = {}
                my_chat_id = tb.get_updates()[-1].message.chat.id
                try:
                    my_sender = tb.get_updates()[-1].message.json['from']['username']
                except Exception as e:
                    print(e)
                    my_sender = 'anonymous'
                my_msg_date = time.ctime(tb.get_updates()[-1].message.date)
                my_msg_consists = tb.get_updates()[-1].message.text.split('/tokenize_korean@tokenize_sent_bot')[1]
                my_tokenized_msg = my_msg_consists.lower().split()
                result_dict = {'chat_id': my_chat_id, 'sender': my_sender, 'msg_date': my_msg_date, 'msg': my_msg_consists, 'tokenized_msg': my_tokenized_msg}
                tb.send_message(my_chat_id, 'мудак. сукапетух ' + "\n" + str(result_dict))
        except Exception as e:
            print("Msg error check")
            print(e)



# тут весь процесс телеграм-апи
def main():
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