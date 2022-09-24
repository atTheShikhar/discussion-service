from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends
from typing import Optional, Union
from . import orms
from . import actions
from .utils import check_pass, gen_token, decode_token, generate_filename, is_valid_image_file, upload_file

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

    jwtToken = gen_token({"user_id": user[0], "uname": user[1], "name": user[2]})
    return {"token": jwtToken}


@router.post("/add-post")
async def ask_a_question(
    title: str = Form(),
    desc: Optional[str] = Form(None),
    image: Union[UploadFile, None] = File(default=None),
    token_data = Depends(decode_token)
):
    user_id = token_data["user_id"]
    has_media = image != None
    actions.save_post(title, desc, user_id, has_media)
    post_id = actions.get_last_saved_post_id(user_id)

    if has_media and is_valid_image_file(image.content_type):
        formatted_filename = generate_filename(image.filename)
        upload_file(image.file, formatted_filename)
        actions.save_post_media(formatted_filename, post_id)

    return orms.GenericResp(message="Question posted successfully!")


@router.post("/add-comment")
async def add_comment_to_post(req: orms.CommentReq, token_data = Depends(decode_token)):
    user_id = token_data["user_id"]

    if not actions.check_post_exists(req.post_id):
        raise HTTPException(400, "Invalid request!")

    actions.add_comment(req.text, req.post_id, user_id)
    actions.inc_comment_count(req.post_id)
    return orms.GenericResp(message="Comment added successfully!")


@router.post("/toggle-like")
async def toggle_like(req: orms.ToggleLikeReq, token_data = Depends(decode_token)):
    user_id = token_data["user_id"]
    entity = req.entity
    ent_id = req.ent_id

    if ((entity == "post" and not actions.check_post_exists(ent_id)) or 
        (entity == "comment" and not actions.check_comment_exists(ent_id))):
        raise HTTPException(400, f"This {entity} does not exists anymore!")

    is_liked = actions.check_like_exists(entity, ent_id, user_id)
    actions.toggle_like(entity, ent_id, user_id, not is_liked)
    actions.toggle_like_count(entity, ent_id, not is_liked)
    return orms.GenericResp(message=f"{entity.capitalize()} {'disliked' if is_liked else 'liked'}!")

