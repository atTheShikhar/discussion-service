from pydantic import BaseModel, validator

from app.utils import hash_pass

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
