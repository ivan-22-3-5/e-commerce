from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.reviews import ReviewCRUD
from src.crud.products import ProductCRUD
from src.schemas.review import ReviewIn, ReviewUpdate
from src.schemas.filtration import PaginationParams
from src.db.models import Review as ReviewModel
from src.custom_exceptions import (
    ResourceDoesNotExistError,
    NotEnoughRightsError,
    ResourceAlreadyExistsError,
)


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.review_crud = ReviewCRUD(db)
        self.product_crud = ProductCRUD(db)

    async def _update_product_rating(self, product_id: int):
        average_rating = await self.review_crud.calculate_average_rating_for_product(
            product_id
        )
        await self.product_crud.update_product_rating(product_id, average_rating)
        await self.db.flush()

    async def create_review(
        self, review_data: ReviewIn, user_id: int, product_id: int
    ) -> ReviewModel:
        product = await self.product_crud.get(product_id, on_not_found="return-none")
        if not product:
            raise ResourceDoesNotExistError(f"Product with ID {product_id} not found.")

        existing_review = await self.review_crud._get_one(
            (ReviewModel.user_id == user_id) & (ReviewModel.product_id == product_id)
        )
        if existing_review:
            raise ResourceAlreadyExistsError("You have already reviewed this product.")

        new_review = await self.review_crud.create_review(
            review_data, user_id, product_id
        )
        await self._update_product_rating(product_id)
        await self.db.refresh(
            new_review, attribute_names=["user"]
        )  # Ensure user is loaded for ReviewOut
        return new_review

    async def get_reviews_for_product(
        self, product_id: int, pagination: PaginationParams
    ) -> list[ReviewModel]:
        product = await self.product_crud.get(product_id, on_not_found="return-none")
        if not product:
            raise ResourceDoesNotExistError(f"Product with ID {product_id} not found.")

        return await self.review_crud.get_reviews_by_product_id(product_id, pagination)

    async def get_reviews_by_user(
        self, user_id: int, pagination: PaginationParams
    ) -> list[ReviewModel]:
        return await self.review_crud.get_reviews_by_user_id(user_id, pagination)

    async def delete_review(self, review_id: int, current_user_id: int, is_admin: bool):
        review_to_delete = await self.review_crud.get(
            review_id, on_not_found="return-none"
        )

        if not review_to_delete:
            raise ResourceDoesNotExistError(f"Review with ID {review_id} not found.")

        if not is_admin and review_to_delete.user_id != current_user_id:
            raise NotEnoughRightsError(
                "You do not have permission to delete this review."
            )

        product_id_of_deleted_review = review_to_delete.product_id

        await self.review_crud.delete(key=review_id)
        await self._update_product_rating(product_id_of_deleted_review)

    async def update_my_review(
        self, review_id: int, review_update_data: ReviewUpdate, current_user_id: int
    ) -> ReviewModel:
        review_to_update = await self.review_crud.get(
            review_id, on_not_found="return-none"
        )

        if not review_to_update:
            raise ResourceDoesNotExistError(f"Review with ID {review_id} not found.")

        if review_to_update.user_id != current_user_id:
            raise NotEnoughRightsError(
                "You do not have permission to update this review."
            )

        updated_review = await self.review_crud.update_review_by_id(
            review_id, review_update_data
        )

        if not updated_review:
            raise ResourceDoesNotExistError(
                f"Failed to update review with ID {review_id}."
            )  # Should not happen

        rating_changed = (
            review_update_data.rating is not None
            and review_update_data.rating != review_to_update.rating
        )
        if rating_changed:
            await self._update_product_rating(updated_review.product_id)

        await self.db.refresh(updated_review, attribute_names=["user"])
        return updated_review
