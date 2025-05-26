from fastapi import APIRouter, status, Depends

from src.schemas.order import OrderOut
from src.schemas.review import ReviewOut
from src.schemas.user import UserOut
from src.schemas.filtration import PaginationParams
from src.deps import CurrentUserDep, OrderServiceDep, ReviewServiceDep

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(user: CurrentUserDep):
    return user


@router.get("/me/orders", response_model=list[OrderOut], status_code=status.HTTP_200_OK)
async def get_my_orders(user: CurrentUserDep, order_service: OrderServiceDep):
    return await order_service.get_by_user(user.id)


@router.get(
    "/me/reviews", response_model=list[ReviewOut], status_code=status.HTTP_200_OK
)
async def get_my_reviews(
    user: CurrentUserDep,
    review_service: ReviewServiceDep,
    pagination: PaginationParams = Depends(),
):
    reviews = await review_service.get_reviews_by_user(
        user_id=user.id, pagination=pagination
    )
    return reviews
