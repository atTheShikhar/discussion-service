from fastapi import APIRouter, HTTPException
from . import orms
from . import actions
from .utils import check_pass, gen_token

router = APIRouter(tags=["Discussion Apis"])

@router.get("/ping")
def ping():
    return "pong!"

@router.post("/register")
async def register_new_user(req: orms.RegisterReq):
    is_uname_available = actions.check_uname_available(req.uname)
    if not is_uname_available:
        raise HTTPException(409, "Username is taken, Please choose a different username!")
    actions.save_user(req)
    return orms.GenericResp(message="Account created successfully, You can login now!")

@router.post("/login")
async def register_new_user(req: orms.LoginReq):
    user = actions.get_user(req.uname)
    if (not user) or (not check_pass(req.password, user[4])):
        raise HTTPException(401, "Invalid username or password!")
    jwtToken = gen_token({"uid": user[0], "uname": user[1], "name": user[2]})
    return {"token": jwtToken}
