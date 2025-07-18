from typing import Annotated, Any
import secrets
import uuid
from time import time

from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix="/demo_auth", tags=["Demo Auth"])

security = HTTPBasic()


@router.get("/basic_auth")
def demo_basic_auth_credentials(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    return {
        "message": "Hi!",
        "username": credentials.username,
        "password": credentials.password,
    }


username_to_password = {
    "admin": "admin",
    "john": "password",
}


static_auth_token_to_username = {
    "c3016df2f9ec7338eca94810f40a7a84": "admin",
    "75f1f12a0496ef97a0aa25513b0009ab": "johm",
}


def get_username_by_static_auth_token(
    static_token: str = Header(alias="x-static-auth-token"),
) -> str:
    if username := static_auth_token_to_username.get(static_token):
        return username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid"
    )


def get_auth_user_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> str:
    unautihed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    current_password = username_to_password.get(credentials.username)
    if credentials.username not in username_to_password:
        raise unautihed_exc

    # secrets
    if not secrets.compare_digest(
        credentials.password.encode("utf-8"),
        current_password.encode("utf-8"),
    ):
        raise unautihed_exc

    return credentials.username


@router.get("/basic-auth-username/")
def demo_basic_auth_username(auth_username: str = Depends(get_auth_user_username)):
    return {"message": f"Hi {auth_username}!", "username": auth_username}


@router.get("/some-http-header-auth/")
def demo_auth_some_http_header(
    username: str = Depends(get_username_by_static_auth_token),
):
    return {"message": f"Hi {username}!", "username": username}


COOKIES: dict[str, dict[str, Any]] = {}
COOKIE_SESSION_TO_KEY = "web-app-session-id"


def generate_session_id() -> str:
    return uuid.uuid4().hex


def get_session_data(session_id: str = Cookie(alias=COOKIE_SESSION_TO_KEY)) -> dict:
    if session_id not in COOKIES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="not authenticated",
        )

    return COOKIES[session_id]


@router.post("/login-cookie/")
def demo_auth_login_set_cookie(
    response: Response,
    # auth_username: str = Depends(get_auth_user_username),
    username: str = Depends(get_username_by_static_auth_token),
):
    session_id = generate_session_id()
    COOKIES[session_id] = {"username": username, "login_at": int(time())}
    response.set_cookie(COOKIE_SESSION_TO_KEY, session_id)

    return {"result": "ok"}


@router.get("/check-cookie/")
def demo_auth_check_cookie(user_session_data: dict = Depends(get_session_data)):
    username = user_session_data["username"]
    return {
        "message": f"Hi, {username}!",
        **user_session_data,
    }


@router.get("/logout-cookie/")
def demo_auth_logout_cookie(
    response: Response,
    session_id: str = Cookie(alias=COOKIE_SESSION_TO_KEY),
    user_session_data: dict = Depends(get_session_data),
):
    COOKIES.pop(session_id)
    response.delete_cookie(COOKIE_SESSION_TO_KEY)
    username = user_session_data["username"]
    return {
        "message": f"Bye, {username}!",
    }
