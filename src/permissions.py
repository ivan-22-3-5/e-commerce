from fastapi import Depends

from src.deps import CurrentUserDep
from src.custom_exceptions import NotEnoughRightsError


def assert_admin_role(user: CurrentUserDep):
    if not user.is_admin:
        raise NotEnoughRightsError("Only admin user can access this endpoint")


AdminRole = Depends(assert_admin_role)
