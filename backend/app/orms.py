from enum import Enum
from optparse import Option
from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel, validator

from .utils import hash_pass, MEDIA_BASE_URL

class LoginReq(BaseModel):
    uname: str
    password: str

class RegisterReq(LoginReq):
    name: str

    @validator("password")
    def validate_and_hash_password(cls, v:str):
        if len(v) < 6:
            raise ValueError("Password must contain more than 6 characters!")
        return hash_pass(v)

class GenericResp(BaseModel):
    message: str

class CommentReq(BaseModel):
    text: str
    post_id: int

class Entities(str, Enum):
    post = "post"
    comment = "comment"

class ToggleLikeReq(BaseModel):
    entity: Entities
    ent_id: int # this can be post_id or comment_id based on the value of entity

class User(BaseModel):
    user_id: int
    uname: str
    name: str
    joined_at: Optional[datetime]

class PostBase(BaseModel):
    post_id: int
    title: str
    like_count: int
    comment_count: int
    has_media: bool
    text: Optional[str]
    created_at: Optional[datetime]
    user: Optional[User]

class PostExtended(PostBase):
    media: Optional[list[str]]
    is_liked: Optional[bool] # will determine whether the person requesting a post has liked it or not.

    @validator("media")
    def add_base_url(cls, v:Optional[list[str]]):
        if v != None:
            valid_medias = list(map(lambda filename: f"{MEDIA_BASE_URL}{filename}", v))
            return valid_medias
        return v

class SearchPostOptions(str, Enum):
    author = "author" # Search post by uname or name columns
    title = "title" # by title column
    text = "text" # by text column
