import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header, status
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
    static_token: str = Header(alias="x-static-auth-token")
) -> str:
    if username:= static_auth_token_to_username.get(static_token):
        return username
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid"
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
def demo_auth_some_http_header(username: str = Depends(get_username_by_static_auth_token)):
    return {"message": f"Hi {username}!", "username": username}


