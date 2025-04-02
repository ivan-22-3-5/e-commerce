from typing import Optional

from fastapi import APIRouter, status

from src.crud import CartCRUD
from src.schemas.cart import CartOut
from src.schemas.item import ItemIn
from src.deps import CurrentUserDep, SessionDep

router = APIRouter(
    prefix='/cart',
    tags=['users']
)


@router.get('', response_model=CartOut, status_code=status.HTTP_200_OK)
async def get_my_cart(user: CurrentUserDep, db: SessionDep):
    return await CartCRUD.get_cart(user.id, db)


@router.post('/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def add_item_to_cart(user: CurrentUserDep, item: ItemIn, db: SessionDep):
    await CartCRUD.add_item(user.id, item, db)
    return await CartCRUD.get_cart(user.id, db)


@router.delete('/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def remove_item_from_cart(user: CurrentUserDep, item: ItemIn, db: SessionDep):
    await CartCRUD.remove_item(user.id, item, db)
    return await CartCRUD.get_cart(user.id, db)


@router.post('/clear', response_model=CartOut, status_code=status.HTTP_200_OK)
async def clear_cart(user: CurrentUserDep, db: SessionDep):
    await CartCRUD.clear(user.id, db)
    return await CartCRUD.get_cart(user.id, db)
