# pip install psycopg2-binary
# sudo -i -u postgres учетка постгрес
# help - помощь
# CREATE ROLE admen_role;
# CREATE DATABASE token_bot;
# CREATE USER admen WITH ENCRYPTED PASSWORD 'admen'
# GRANT ALL ON DATABASE token_bot TO admen;
# postgres=# \c sales
# You are now connected to database "sales" as user "ubuntu".
# sales=#
# createdb tokenizer
#
# service postgresql status
import psycopg2


conn = psycopg2.connect(dbname='token_bot', user='admen',
                        password='admen', host='127.0.0.1')

# create_jpn_table =         """
#         CREATE TABLE msg_japanese (
#             msg_id INT PRIMARY KEY,
#             msg_time TIMESTAMP,
#             sender VARCHAR(255),
#             chat_id INT,
#             msg VARCHAR,
#             tokenized_msg VARCHAR
#         )
#         """

# insert_jpn_table = """
#         INSERT INTO msg_japanese VALUES (1, '2011-05-16 15:36:38', 'test_bot', 21, 'look at me', 'look, at, me');
#
# """

# create_user_table =         """
#         CREATE TABLE users (
#             nickname VARCHAR(25) PRIMARY KEY,
#             group_name VARCHAR(15),
#             name VARCHAR(25)
#
#         )
#         """

create_bot_table =         """
        CREATE TABLE bots (
            botname VARCHAR(25) PRIMARY KEY,
            server_user VARCHAR(25)
        )
        """

#select_jpn = """(SELECT * FROM msg_japanese)"""


cur = conn.cursor()
# create table one by one
cur.execute(create_bot_table)
#result = cur.fetchall()
# close communication with the PostgreSQL database server
#print(result)
# commit the changes
conn.commit()
conn.close()