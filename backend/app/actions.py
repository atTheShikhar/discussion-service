import mysql.connector
from .utils import creds_dict
from . import orms

sql_conn = mysql.connector.connect(
    user=creds_dict["USER"],
    password=creds_dict["PASSWORD"],
    host=creds_dict["HOST"],
    db=creds_dict["DB"],
)
sql_conn.autocommit = True
cursor = sql_conn.cursor()

def persist_connection(func):
    def inner(*args, **kwargs):
        global sql_conn
        global cursor
        if not sql_conn.is_connected():
            sql_conn = mysql.connector.connect(
                user=creds_dict["USER"],
                password=creds_dict["PASSWORD"],
                host=creds_dict["HOST"],
                db=creds_dict["DB"]
            )
            sql_conn.autocommit = True
            cursor = sql_conn.cursor()
        return func(*args, **kwargs)
    return inner


@persist_connection
def check_uname_available(uname: str):
    cursor.execute("SELECT COUNT(`uid`) FROM `users` WHERE uname=%s LIMIT 1", (uname,))
    count = cursor.fetchone()[0]
    return count == 0

@persist_connection
def save_user(user: orms.RegisterReq):
    cursor.execute("INSERT INTO `users`(uname, name, password) VALUES(%(uname)s, %(name)s, %(password)s)", user.dict())

@persist_connection
def get_user(uname: str):
    cursor.execute("SELECT * FROM `users` WHERE uname=%s LIMIT 1", (uname,))
    user = cursor.fetchone()
    return user