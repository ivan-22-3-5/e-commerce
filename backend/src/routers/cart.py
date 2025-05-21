from typing import Optional

from fastapi import APIRouter, status

from src.schemas.cart import CartOut
from src.schemas.item import ItemIn
from src.deps import CurrentUserDep, CartServiceDep

router = APIRouter(
    prefix='/cart',
    tags=['cart']
)


@router.get('', response_model=CartOut, status_code=status.HTTP_200_OK)
async def get_my_cart(user: CurrentUserDep, cart_service: CartServiceDep):
    return await cart_service.get_cart(user.id)


@router.post('/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def add_item_to_cart(user: CurrentUserDep, item: ItemIn, cart_service: CartServiceDep):
    await cart_service.add_item(user.id, item)
    return await cart_service.get_cart(user.id)


@router.delete('/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def remove_item_from_cart(user: CurrentUserDep, item: ItemIn, cart_service: CartServiceDep):
    await cart_service.remove_item(user.id, item)
    return await cart_service.get_cart(user.id)


@router.post('/clear', response_model=CartOut, status_code=status.HTTP_200_OK)
async def clear_cart(user: CurrentUserDep, cart_service: CartServiceDep):
    await cart_service.clear_cart(user.id)
    return await cart_service.get_cart(user.id)
