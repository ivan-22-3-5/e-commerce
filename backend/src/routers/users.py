from typing import Optional

from fastapi import APIRouter, status

from src.crud import ReviewCRUD, CartCRUD, AddressCRUD, OrderCRUD
from src.schemas.address import AddressOut
from src.schemas.cart import CartOut
from src.schemas.item import ItemIn
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


@router.get('/me/cart', response_model=CartOut, status_code=status.HTTP_200_OK)
async def get_my_cart(user: CurrentUserDep, db: SessionDep):
    return await CartCRUD.get(user.id, db)


@router.post('/me/cart/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def add_item_to_cart(user: CurrentUserDep, item: ItemIn, db: SessionDep):
    return await CartCRUD.add_item(user.id, item, db)


@router.delete('/me/cart/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def remove_item_from_cart(user: CurrentUserDep, item: ItemIn, db: SessionDep):
    return await CartCRUD.remove_item(user.id, item, db)


@router.post('/me/cart/clear', response_model=CartOut, status_code=status.HTTP_200_OK)
async def clear_cart(user: CurrentUserDep, db: SessionDep):
    return await CartCRUD.clear(user.id, db)
