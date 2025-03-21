from fastapi import APIRouter, status

from src.crud import ReviewsCRUD, ProductCRUD
from src.custom_exceptions import NotEnoughRightsError
from src.db.models import Review
from src.deps import CurrentUserDep, SessionDep
from src.permissions import ConfirmedEmail
from src.schemas.message import Message
from src.schemas.review import ReviewIn

router = APIRouter(
    prefix='/reviews',
    tags=['reviews']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=Message,
             dependencies=[ConfirmedEmail])
async def create_review(user: CurrentUserDep, product_id: int, review: ReviewIn, db: SessionDep):
    product = await ProductCRUD.get(product_id, db)
    await ReviewsCRUD.create(Review(
        product_id=product.id,
        user_id=user.id,
        **review.model_dump(),
    ), db)
    return Message(message="Review has been successfully added")


@router.delete('/{review_id}', status_code=status.HTTP_200_OK, response_model=Message)
async def delete_review(review_id: int, user: CurrentUserDep, db: SessionDep):
    def predicate(review: Review):
        if review.user_id != user.id:
            raise NotEnoughRightsError("Only the owner can delete the review")
        return True

    await ReviewsCRUD.delete(review_id, db, predicate=predicate)
    return Message(message="Review has been successfully deleted")
