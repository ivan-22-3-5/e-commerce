from functools import wraps

from src.custom_exceptions import NotEnoughRightsError


# TODO: remove decorator, rewrite permission system as fast api based dependencies
def admin_path(f):
    @wraps(f)
    async def wrapper(user, *args, **kwargs):
        if not user.is_admin:
            raise NotEnoughRightsError("Only admin user can access this endpoint")
        return await f(user, *args, **kwargs)

    return wrapper


def confirmed_email_required(f):
    @wraps(f)
    async def wrapper(user, *args, **kwargs):
        if not user.is_confirmed:
            raise NotEnoughRightsError("Only user with a confirmed email can access this endpoint")
        return await f(user, *args, **kwargs)

    return wrapper
