from typing import Optional
import mysql.connector
from .utils import creds_dict, paginate, sqltuple2dict, num_list2comma_string
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
    cursor.execute("SELECT COUNT(`user_id`) FROM `users` WHERE uname=%s LIMIT 1", (uname,))
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

@persist_connection
def save_post(title: str, text: Optional[str], user_id: int, has_media: bool):
    cursor.execute(
        "INSERT INTO posts(title, `text`, user_id, has_media) VALUES(%s, %s, %s, %s)", 
        (title, text, user_id, has_media,)
    )

@persist_connection
def get_last_saved_post_id(user_id: int):
    cursor.execute("SELECT post_id FROM posts WHERE user_id=%s ORDER BY post_id DESC LIMIT 1", (user_id,))
    post_id = cursor.fetchone()[0]
    return post_id

@persist_connection
def save_post_media(file_name: str, post_id: int):
    cursor.execute(
        "INSERT INTO post_media(file_name, post_id) VALUES(%s, %s)", 
        (file_name, post_id,)
    )

@persist_connection
def check_post_exists(post_id: int):
    cursor.execute("SELECT post_id FROM posts WHERE post_id=%s LIMIT 1", (post_id,))
    data = cursor.fetchall()
    return bool(data)

@persist_connection
def check_comment_exists(comment_id: int):
    cursor.execute("SELECT comment_id FROM `comments` WHERE comment_id=%s LIMIT 1", (comment_id,))
    data = cursor.fetchall()
    return bool(data)

@persist_connection
def add_comment(text: str, post_id: int, user_id: int):
    cursor.execute(
        "INSERT INTO `comments`(`text`, post_id, user_id) VALUES(%s, %s, %s)",
        (text, post_id, user_id,)
    )

@persist_connection
def inc_comment_count(post_id: int):
    cursor.execute("UPDATE posts SET comment_count = comment_count + 1 WHERE post_id=%s", (post_id,))

@persist_connection
def check_like_exists(entity: orms.Entities, ent_id: int, user_id: int):
    cursor.execute(
        f"SELECT EXISTS(SELECT * FROM {entity}_likes WHERE {entity}_id = %s AND user_id = %s)",
        (ent_id, user_id,)
    )
    return cursor.fetchone()[0]

@persist_connection
def toggle_like_count(entity: orms.Entities, ent_id: int, increment: bool):
    cursor.execute(
        f"UPDATE {entity}s SET like_count = like_count {'+' if increment else '-'} 1 WHERE {entity}_id=%s", 
        (ent_id,)
    )

@persist_connection
def toggle_like(entity: orms.Entities, ent_id: int, user_id: int, add_like: bool):
    if add_like:
        cursor.execute(f"INSERT INTO {entity}_likes({entity}_id, user_id) VALUES(%s, %s)", (ent_id, user_id,))
    else:
        cursor.execute(f"DELETE FROM {entity}_likes WHERE {entity}_id = %s AND user_id = %s", (ent_id, user_id,))

@persist_connection
def get_user_by_userid_list(userids: list[int]):
    cursor.execute(
        f"SELECT user_id, `uname`, `name`, joined_at FROM `users` WHERE user_id IN ({num_list2comma_string(userids)})"
    )
    data = sqltuple2dict(cursor)
    return [orms.User(**usr) for usr in data]

# Parital text search to find a user by username or name.
@persist_connection
def search_user_single(term: str):
    term = f"%{term}%"
    cursor.execute(
        "SELECT user_id, `uname`, `name`, joined_at FROM `users` WHERE `uname` LIKE %s OR `name` LIKE %s LIMIT 1", 
        (term, term,)
    )
    data = sqltuple2dict(cursor)
    return orms.User(**data[0]) if len(data) > 0 else None

# Gets the post list in descending order. i.e. Latest posts are shown first
@persist_connection
def get_posts_by_userid(user_id: int, page: int, limit: int):
    offset = paginate(page, limit)
    cursor.execute(
        "SELECT * FROM posts WHERE user_id=%s ORDER BY post_id DESC LIMIT %s OFFSET %s",
        (user_id, limit, offset,)
    )
    data = sqltuple2dict(cursor)
    return data

# Natural language full text search to find posts based on certain terms.
# Sorted based based on relevance
@persist_connection
def full_text_post_search(column: str, terms: str, page: int, limit: int):
    offset = paginate(page, limit)
    cursor.execute(
        f"SELECT * FROM posts WHERE MATCH({column}) AGAINST(%s) LIMIT %s OFFSET %s",
        (terms, limit, offset,)
    )
    data = sqltuple2dict(cursor)
    return data
