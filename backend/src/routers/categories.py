from fastapi import APIRouter, status

from src.permissions import AdminRole
from src.schemas.category import CategoryIn, CategoryOut
from src.schemas.message import Message
from src.deps import CategoryServiceDep

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=CategoryOut, dependencies=[AdminRole])
async def create_category(category: CategoryIn, category_service: CategoryServiceDep):
    return await category_service.create_category(category)


@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminRole])
async def delete_category(category_id: int, category_service: CategoryServiceDep):
    await category_service.delete_category(category_id)


@router.post('/{category_id}/products/{product_id}', status_code=status.HTTP_201_CREATED, dependencies=[AdminRole])
async def link_category_to_product(category_id: int, product_id: int, category_service: CategoryServiceDep):
    category_service.link_category_to_product(category_id, product_id)

    return Message(message=f"Category {category_id} has been successfully linked to product with id {product_id}")
