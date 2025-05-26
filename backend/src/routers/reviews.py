from fastapi import APIRouter, status, Depends, HTTPException

from src.deps import CurrentUserDep, ReviewServiceDep
from src.schemas.review import ReviewIn, ReviewOut, ReviewUpdate
from src.schemas.filtration import PaginationParams
from src.custom_exceptions import ResourceDoesNotExistError, NotEnoughRightsError, ResourceAlreadyExistsError

router = APIRouter(
    prefix="/products/{product_id}/reviews",
    tags=['Product Reviews']
)

reviews_router_individual = APIRouter(
    prefix="/reviews",
    tags=['Reviews (Individual Operations)']
)


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_product_review_endpoint(
        product_id: int,
        review_in: ReviewIn,
        current_user: CurrentUserDep,
        review_service: ReviewServiceDep
):
    try:
        review = await review_service.create_review(
            review_data=review_in,
            user_id=current_user.id,
            product_id=product_id
        )
        return review
    except ResourceDoesNotExistError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ResourceAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.get("", response_model=list[ReviewOut], status_code=status.HTTP_200_OK)
async def get_reviews_for_product_endpoint(
        product_id: int,
        pagination: PaginationParams = Depends(),
        review_service: ReviewServiceDep = Depends()
):
    try:
        reviews = await review_service.get_reviews_for_product(product_id=product_id, pagination=pagination)
        return reviews
    except ResourceDoesNotExistError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@reviews_router_individual.put("/{review_id}", response_model=ReviewOut, status_code=status.HTTP_200_OK)
async def update_my_review_endpoint(
        review_id: int,
        review_update_data: ReviewUpdate,
        current_user: CurrentUserDep,
        review_service: ReviewServiceDep
):
    try:
        updated_review = await review_service.update_my_review(
            review_id=review_id,
            review_update_data=review_update_data,
            current_user_id=current_user.id
        )
        return updated_review
    except ResourceDoesNotExistError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRightsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@reviews_router_individual.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_review_endpoint(
        review_id: int,
        current_user: CurrentUserDep,
        review_service: ReviewServiceDep
):
    try:
        await review_service.delete_review(
            review_id=review_id,
            current_user_id=current_user.id,
            is_admin=current_user.is_admin
        )
    except ResourceDoesNotExistError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotEnoughRightsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))