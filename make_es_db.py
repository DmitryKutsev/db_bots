from elasticsearch import Elasticsearch
# cd elasticsearch-7.6.1/
# ./bin/elasticsearch
es=Elasticsearch()

settings = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "kuromoji_search": {
                    "type": "kuromoji_tokenizer",
                    "mode": "search"
                }
            },

            "analyzer": {
                "my_analyzer": {
                    "type": "custom",
                    "tokenizer": "kuromoji_search"
                }
            }
        }
    }
}

es.indices.create(index="japanese")

#добавить маппинг
mapit = {"msg": {"properties": {"date": {"type": "date", "format": "YYYY:MM:DD"},
                                    "time": {"type": "date", "format": "HH:mm"},
                                    "rubrics": {"type": "text", "analyzer": "keyword"},
                                    "text": {"type": "text", "analyzer": "keyword"},

                                    "title": {"type": "text", "analyzer": "keyword"}}}}


# time.strftime("%x", datetime.isoformat(1584916284))
es.indices.create(index="japanese")
mapit_jap = {

    "msg": {
        "properties": {"msg_date": {"type": "date", "format": "YYYY-MM-DD"},
                                    "msg_time": {"type": "date", "format": "HH:mm"},
                                    "msg_datetime": {"type": "date", "format": "YYYY-MM-DD HH:mm"},
                                    "sender": {"type": "text", "analyzer": "keyword"},
                                    "chat_id": {"type": "text", "analyzer": "keyword"},
                                    "msg": {"type": "text", "analyzer": "keyword"},
                                    "tokenized_msg": {"type": "text", "analyzer": "keyword"
                                                      }}}}

es.indices.put_mapping(index='japanese', doc_type='msg', body=mapit_jap, include_type_name=True)

#добавление документа в индекс
art = {"date": "1111:11:11",
         "time":"00:00",
         "rubrics":"chlen govno",
         "text":"grotesque",
         "title":"xuy!"}
es.index(index="nplus1", doc_type='article', body=art)
#поиск по документам (здесь все)
es.search(index="nplus1", body={"query": {"match_all": {}}})
#поиск по документам (с условием)
es.search(index="nplus1", body={"query": {"match": {"rubrics": "chlen govno"}}})
#удаление документов(!) по запросу
es.delete_by_query(index="nplus1", body={"query": {"match": {"rubrics": "chlen govno"}}})
#грохнуть индекс
es.indices.delete("japanese")