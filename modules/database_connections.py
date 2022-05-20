import sqlite3
import os
import datetime

def current_time():
    return str(datetime.datetime.now())[:19]

def connect_db():
    db_name = "assets.db"
    if not os.path.exists(db_name):
        print("[-] Database Does Not Exists. Creating it with new information.")
        connection = sqlite3.connect(db_name)
        connection.execute('''CREATE TABLE "assets" (
                                "id"	INTEGER,
                                "asset"	TEXT NOT NULL,
                                "live"	INTEGER DEFAULT 0,
                                "status_code"	INTEGER DEFAULT 0,
                                "content_length"	INTEGER DEFAULT 0,
                                "created_time"	TEXT DEFAULT '1999-01-01 00:00:00',
                                PRIMARY KEY("id" AUTOINCREMENT)
                            );''')
        connection.commit()

    connection = sqlite3.connect(db_name)

    return connection

def insert_into_database(subdomain_information):
    # {'url': 'sps.am.sony.com', 'live': 0, 'status_code': 0, 'content_length': 0}
    query = "Insert Into assets (asset, live, status_code, content_length, created_time) VALUES (?,?,?,?,?)"

    asset = subdomain_information["url"]
    live = subdomain_information["live"]
    status_code = subdomain_information["status_code"]
    content_length = subdomain_information["content_length"]
    created_time = current_time()
    values = [asset, live, status_code, content_length, created_time]

    connection = connect_db()
    cursor = connection.execute(query, values)
    connection.commit()
    inserted_rows = cursor.rowcount
    connection.close()