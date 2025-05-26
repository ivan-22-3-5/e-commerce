from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.crud.base import Creatable, Retrievable, Deletable, Updatable
from src.db import models
from src.schemas.filtration import PaginationParams
from src.schemas.review import ReviewIn, ReviewUpdate


class ReviewCRUD(Creatable, Retrievable, Deletable, Updatable):
    model = models.Review
    key = models.Review.id

    async def create_review(
        self, review_data: ReviewIn, user_id: int, product_id: int
    ) -> models.Review:
        new_review_obj = self.model(
            **review_data.model_dump(), user_id=user_id, product_id=product_id
        )
        return await self.create(new_review_obj)

    async def get_reviews_by_product_id(
        self, product_id: int, pagination: PaginationParams
    ) -> list[models.Review]:
        query = (
            select(self.model)
            .where(self.model.product_id == product_id)
            .options(joinedload(self.model.user))
            .order_by(self.model.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_reviews_by_user_id(
        self, user_id: int, pagination: PaginationParams
    ) -> list[models.Review]:
        query = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(
                joinedload(self.model.product).selectinload(models.Product.images),
                joinedload(self.model.user),
            )
            .order_by(self.model.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_review_by_id(
        self, review_id: int, review_update_data: ReviewUpdate
    ) -> models.Review | None:
        return await self.update(key=review_id, obj_update=review_update_data)

    async def calculate_average_rating_for_product(self, product_id: int) -> float:
        query = select(
            func.coalesce(func.avg(self.model.rating), 0.0).label("average_rating")
        ).where(self.model.product_id == product_id)
        result = await self.db.execute(query)
        average_rating = result.scalar_one_or_none()
        return round(average_rating, 1) if average_rating is not None else 0.0
