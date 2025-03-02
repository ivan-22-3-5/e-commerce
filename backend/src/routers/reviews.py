from fastapi import APIRouter, status

from src.constraints import confirmed_email_required
from src.crud import reviews, products
from src.custom_exceptions import ResourceDoesNotExistError, NotEnoughRightsError
from src.deps import cur_user_dependency, db_dependency
from src.schemas.message import Message
from src.schemas.review import ReviewIn

router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)


@confirmed_email_required
@router.post('', status_code=status.HTTP_201_CREATED, response_model=Message)
async def create_review(user: cur_user_dependency, product_id: int, review: ReviewIn, db: db_dependency):
    if not await products.get_by_id(product_id, db):
        raise ResourceDoesNotExistError("Product with the given id does not exist")
    await reviews.create(product_id, user.id, review, db)
    return Message(message="Review has been successfully added")


@router.delete('/{review_id}', status_code=status.HTTP_200_OK, response_model=Message)
async def delete_review(review_id: int, user: cur_user_dependency, db: db_dependency):
    if (review := await reviews.get_by_id(review_id, db)) is None:
        raise ResourceDoesNotExistError("Review with the given id does not exist")
    if review.user_id != user.id:
        raise NotEnoughRightsError("Only the owner can delete the review")
    await reviews.delete(review_id, db)
    return Message(message="Review has been successfully deleted")
