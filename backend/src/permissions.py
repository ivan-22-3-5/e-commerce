from fastapi import Depends

from deps import CurrentUserDep
from src.custom_exceptions import NotEnoughRightsError


def assert_admin_role(user: CurrentUserDep):
    if not user.is_admin:
        raise NotEnoughRightsError("Only admin user can access this endpoint")


def assert_confirmed_email(user: CurrentUserDep):
    if not user.is_confirmed:
        raise NotEnoughRightsError("Only user with a confirmed email can access this endpoint")


AdminRole = Depends(assert_admin_role)
ConfirmedEmail = Depends(assert_confirmed_email)
