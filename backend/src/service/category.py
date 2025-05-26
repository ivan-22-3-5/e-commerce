from src.crud import ProductCRUD, CategoryCRUD
from src.custom_exceptions import ResourceAlreadyExistsError
from src.db.models import Category
from src.schemas.category import CategoryIn


class CategoryService:
    def __init__(self, category_crud: CategoryCRUD, product_crud: ProductCRUD):
        self.category_crud = category_crud
        self.product_crud = product_crud

    async def create_category(self, category: CategoryIn):
        return await self.category_crud.create(Category(**category.model_dump()))

    async def delete_category(self, category_id: int):
        await self.category_crud.delete(category_id)

    async def link_category_to_product(self, category_id: int, product_id: int):
        category = await self.category_crud.get(category_id)
        product = await self.product_crud.get(product_id)

        if category in await product.awaitable_attrs.categories:
            raise ResourceAlreadyExistsError(
                f"Product is already associated with the {category_id} category"
            )

        product.categories.append(category)
