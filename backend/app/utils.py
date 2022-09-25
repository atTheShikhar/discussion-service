from datetime import datetime, timedelta
import logging
from fastapi import HTTPException, Header
from dotenv import dotenv_values
from jose import jwt
import bcrypt
import boto3
import time, random, string
from typing import Optional
from . import orms

creds_dict = dotenv_values(".env")

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24 # jwt token will be valid for 1 day
JWT_SECRET = creds_dict["JWT_SECRET"]
PWD_ENCODING = "utf-8"
AWS_KEY_ID = creds_dict["AWS_KEY_ID"]
AWS_SECRET_KEY = creds_dict["AWS_SECRET_KEY"]
AWS_S3_BUCKET = creds_dict["AWS_S3_BUCKET"]
MEDIA_BASE_URL = creds_dict["MEDIA_BASE_URL"]

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_KEY
)

def paginate(page, limit):
    offset = (page - 1) * limit
    return offset

# utility function to convert sql query response (tuple) to a dictionary
def sqltuple2dict(conn_cursor):
    columns = [col[0] for col in conn_cursor.description] 
    data = [dict(zip(columns, row)) for row in conn_cursor.fetchall()]
    return data

def generate_filename(input_filename: str):
    ext = input_filename.split(".")[-1]
    curr_time = int(time.time())
    random_string = "".join(random.choices(string.ascii_lowercase+string.digits, k=8))
    return f"{random_string}_{curr_time}.{ext}"

def upload_file(file, filename):
    try:
        s3_client.upload_fileobj(file, AWS_S3_BUCKET, filename)
    except Exception as e:
        logging.exception(e)
        raise HTTPException(500, "Something went wrong, Please try again later!")
    
def gen_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str = Header(...)):
    try: 
        userdata = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return userdata
    except Exception as e:
        logging.exception(e)
        raise HTTPException(401, "Unauthorised!")

def hash_pass(password: str):
    return bcrypt.hashpw(password.encode(PWD_ENCODING), bcrypt.gensalt())

def check_pass(entered_password: str, hashed_password: str):
    return bcrypt.checkpw(entered_password.encode(PWD_ENCODING), hashed_password.encode(PWD_ENCODING))

def is_valid_image_file(content_type: str):
    allowed_types = ["image/jpeg", "image/png"]
    if content_type not in allowed_types:
        raise HTTPException(400, "Invalid image type. Only .png and .jpeg are allowed!")
    return True

def unique_userid_from_posts(posts: list[dict]):
    return set([i["user_id"] for i in posts])

def find_in_dictlist(l: list, k: str, v) -> Optional[dict]:
    for i, dic in enumerate(l):
        if dic.dict()[k] == v: return dic
    return None

num_list2comma_string = lambda a: ','.join(list(map(lambda i: str(i), a)))
# def map_user_to_posts(users: list[orms.User], posts: list[dict]):
