from datetime import timedelta
from typing import Optional, Annotated

from fastapi import APIRouter, status, Body

from src.celery_tasks import send_email_confirmation_email
from src.config import settings
from src.crud import ConfirmationTokenCRUD, UserCRUD, ReviewsCRUD, CartCRUD, AddressCRUD, OrderCRUD
from src.db.models import ConfirmationToken, User, Cart
from src.schemas.address import AddressOut
from src.schemas.cart import CartOut
from src.schemas.item import ItemIn
from src.schemas.message import Message
from src.schemas.order import OrderOut
from src.schemas.review import ReviewOut
from src.schemas.user import UserIn, UserOut
from src.deps import cur_user_dependency, db_dependency
from src.custom_exceptions import ResourceAlreadyExistsError, InvalidTokenError
from src.utils import create_jwt_token, get_user_id_from_jwt

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=Message)
async def create_user(user: UserIn, db: db_dependency):
    if await UserCRUD.get_by_email(user.email, db=db):
        raise ResourceAlreadyExistsError("Email is already registered")
    new_user = await UserCRUD.create(User(**user.model_dump()), db=db)
    await CartCRUD.create(Cart(user_id=new_user.id), db=db)
    confirmation_token = create_jwt_token(user_id=new_user.id,
                                          expires_in=timedelta(minutes=settings.CONFIRMATION_TOKEN_EXPIRE_MINUTES))
    await ConfirmationTokenCRUD.upsert(ConfirmationToken(user_id=new_user.id, token=confirmation_token), db=db)
    send_email_confirmation_email.delay(username=new_user.username,
                                        link=settings.EMAIL_CONFIRMATION_LINK + confirmation_token,
                                        email_address=new_user.email)
    return Message(message="Confirmation email sent")


@router.post('/confirm', status_code=status.HTTP_200_OK, response_model=Message)
async def confirm_email(token: Annotated[str, Body(embed=True)], db: db_dependency):
    user_id = get_user_id_from_jwt(token)
    db_token = await ConfirmationTokenCRUD.get(user_id, db)
    if not (db_token and db_token.token == token):
        raise InvalidTokenError("Invalid confirmation token")
    user = await UserCRUD.get(user_id, db)
    user.is_confirmed = True

    await ConfirmationTokenCRUD.delete(user_id, db)
    return Message(message="The user is confirmed")


@router.get('/me', response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(user: cur_user_dependency):
    return user


@router.get('/me/orders', response_model=list[OrderOut], status_code=status.HTTP_200_OK)
async def get_my_orders(user: cur_user_dependency, db: db_dependency):
    return await OrderCRUD.get_by_user(user.id, db)


@router.get('/me/reviews', response_model=list[ReviewOut], status_code=status.HTTP_200_OK)
async def get_my_reviews(user: cur_user_dependency, db: db_dependency):
    return await ReviewsCRUD.get_by_user(user.id, db)


@router.get('/me/addresses', response_model=list[AddressOut], status_code=status.HTTP_200_OK)
async def get_my_addresses(user: cur_user_dependency, db: db_dependency):
    return await AddressCRUD.get_by_user(user.id, db)


@router.get('/me/cart', response_model=CartOut, status_code=status.HTTP_200_OK)
async def get_my_cart(user: cur_user_dependency, db: db_dependency):
    return await CartCRUD.get(user.id, db)


@router.post('/me/cart/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def add_item_to_cart(user: cur_user_dependency, item: ItemIn, db: db_dependency):
    return await CartCRUD.add_item(user.id, item, db)


@router.delete('/me/cart/items', response_model=Optional[CartOut], status_code=status.HTTP_200_OK)
async def remove_item_from_cart(user: cur_user_dependency, item: ItemIn, db: db_dependency):
    return await CartCRUD.remove_item(user.id, item, db)


@router.post('/me/cart/clear', response_model=CartOut, status_code=status.HTTP_200_OK)
async def clear_cart(user: cur_user_dependency, db: db_dependency):
    return await CartCRUD.clear(user.id, db)
