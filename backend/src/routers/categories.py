from fastapi import APIRouter, status

from src.crud import CategoryCRUD, ProductCRUD
from src.db.models import Category
from src.permissions import AdminRole
from src.schemas.category import CategoryIn, CategoryOut
from src.schemas.message import Message
from src.deps import SessionDep
from src.custom_exceptions import ResourceAlreadyExistsError

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=CategoryOut, dependencies=[AdminRole])
async def create_category(category: CategoryIn, db: SessionDep):
    return await CategoryCRUD.create(Category(**category.model_dump()), db=db)


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminRole])
async def delete_category(category_id: str, db: SessionDep):
    await CategoryCRUD.delete(category_id, db)


@router.post('/{category_id}/products/{product_id}', status_code=status.HTTP_201_CREATED, dependencies=[AdminRole])
async def link_category_to_product(category_id: int, product_id: int, db: SessionDep):
    category = await CategoryCRUD.get(category_id, db)
    product = await ProductCRUD.get(product_id, db)

    if category in await product.awaitable_attrs.categories:
        raise ResourceAlreadyExistsError(f"Product is already associated with the {category_id} category")

    product.categories.append(category)

    return Message(message=f"Category {category_id} has been successfully linked to product with id {product_id}")
