from datetime import datetime, timedelta
from fastapi import HTTPException
from dotenv import dotenv_values
from jose import jwt
import bcrypt

creds_dict = dotenv_values(".env")

JWT_ALGORITHM = "HS256"
JWT_SECRET = creds_dict["JWT_SECRET"]
JWT_EXPIRY_HOURS = 24 # jwt token will be valid for 1 day
PWD_ENCODING = "utf-8"

def gen_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def decode_token(token: str):
    try:
        dict = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return dict
    except Exception as e:
        raise HTTPException(401, "Unauthorized!")

def hash_pass(password: str):
    return bcrypt.hashpw(password.encode(PWD_ENCODING), bcrypt.gensalt())

def check_pass(entered_password: str, hashed_password: str):
    return bcrypt.checkpw(entered_password.encode(PWD_ENCODING), hashed_password.encode(PWD_ENCODING))
