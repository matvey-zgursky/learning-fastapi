from users.schemas import CreatedUser

def create_user(user_in: CreatedUser) -> dict:
    user = user_in.model_dump()
    return {
        'success': True,
        'user': user
    }
