from elasticsearch import Elasticsearch

es=Elasticsearch()

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

es.indices.create(index="russian")
mapit_rus = {

    "msg": {
        "properties": {"msg_date": {"type": "date", "format": "YYYY-MM-DD"},
                                    "msg_time": {"type": "date", "format": "HH:mm"},
                                    "msg_datetime": {"type": "date", "format": "YYYY-MM-DD HH:mm"},
                                    "sender": {"type": "text", "analyzer": "keyword"},
                                    "chat_id": {"type": "text", "analyzer": "keyword"},
                                    "msg": {"type": "text", "analyzer": "keyword"},
                                    "tokenized_msg": {"type": "text", "analyzer": "keyword"
                                                      }}}}

es.indices.put_mapping(index='russian', doc_type='msg', body=mapit_rus, include_type_name=True)