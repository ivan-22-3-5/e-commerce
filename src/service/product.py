from src.config import rules
from src.crud import ProductCRUD
from src.custom_exceptions import LimitExceededError, ResourceDoesNotExistError
from src.db.models import Product
from src.file_storage import FileStorage
from src.schemas.filtration import PaginationParams
from src.schemas.product import ProductUpdate, ProductIn


class ProductService:
    def __init__(self, product_crud: ProductCRUD, file_storage: FileStorage):
        self.product_crud = product_crud
        self.file_storage = file_storage

    async def get_products(self, pagination: PaginationParams = None, is_active: bool = None):
        return await self.product_crud.get_all(pagination=pagination, is_active=is_active)

    async def search_products(self, q: str,
                              categories: list[int] = None,
                              pagination: PaginationParams = None):
        return await self.product_crud.search(q, category_ids=categories, pagination=pagination)

    async def create_product(self, product: ProductIn):
        return await self.product_crud.create(Product(
            **product.model_dump()
        ))

    async def update_product(self, product_id: int, product_update: ProductUpdate):
        return await self.product_crud.update(product_id, product_update)

    async def delete_product(self, product_id: int):
        await self.product_crud.delete(product_id)

    # TODO: add resolution/aspect ratio regulation
    async def add_product_image(self, product_id: int, file: bytes, filename: str):
        product = await self.product_crud.get(product_id)

        if len(product.images) >= rules.MAX_IMAGES_PER_PRODUCT:
            raise LimitExceededError("Product already has the maximum number of images")

        await self.file_storage.save(file, f"{product_id}/{filename}")
        # creating a new list is necessary for sqlalchemy to recognize the change
        product.images = product.images + [filename]

    async def change_product_images(self, product_id: int, images: list[str]):
        product = await self.product_crud.get(product_id)

        current_images = set(product.images)
        new_images = set(images)

        if not new_images.issubset(current_images):
            raise ResourceDoesNotExistError("One or more of the specified images does not exist")

        for filename in current_images - new_images:
            await self.file_storage.delete(f"{product_id}/{filename}")

        product.images = images
