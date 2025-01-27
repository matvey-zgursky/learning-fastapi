from fastapi import APIRouter

from users import crud
from users.schemas import CreatedUser


router = APIRouter(prefix='/users', tags=['users'])


@router.post('/')
def create_user(user: CreatedUser):
    return crud.create_user(user_in=user)