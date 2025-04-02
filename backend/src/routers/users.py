from fastapi import APIRouter, status

from src.crud import ReviewCRUD, AddressCRUD, OrderCRUD
from src.schemas.address import AddressOut
from src.schemas.order import OrderOut
from src.schemas.review import ReviewOut
from src.schemas.user import UserOut
from src.deps import CurrentUserDep, SessionDep

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get('/me', response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(user: CurrentUserDep):
    return user


@router.get('/me/orders', response_model=list[OrderOut], status_code=status.HTTP_200_OK)
async def get_my_orders(user: CurrentUserDep, db: SessionDep):
    return await OrderCRUD.get_by_user(user.id, db)


@router.get('/me/reviews', response_model=list[ReviewOut], status_code=status.HTTP_200_OK)
async def get_my_reviews(user: CurrentUserDep, db: SessionDep):
    return await ReviewCRUD.get_by_user(user.id, db)


@router.get('/me/addresses', response_model=list[AddressOut], status_code=status.HTTP_200_OK)
async def get_my_addresses(user: CurrentUserDep, db: SessionDep):
    return await AddressCRUD.get_by_user(user.id, db)
