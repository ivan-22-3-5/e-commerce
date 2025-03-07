from fastapi import APIRouter, status

from src.constraints import admin_path
from src.crud import CategoryCRUD, ProductCRUD
from src.db.models import Category
from src.schemas.category import CategoryIn
from src.schemas.message import Message
from src.deps import cur_user_dependency, db_dependency
from src.custom_exceptions import ResourceAlreadyExistsError, ResourceDoesNotExistError
from src.schemas.product import ProductOut

router = APIRouter(
    prefix='/categories',
    tags=['categories']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=Message)
@admin_path
async def create_category(user: cur_user_dependency, category: CategoryIn, db: db_dependency):
    if await CategoryCRUD.get(category.name, db):
        raise ResourceAlreadyExistsError("Category with the given name already exists")
    await CategoryCRUD.create(Category(**category.model_dump()), db=db)
    return Message(message=f"Category {category.name} has been successfully created")


@router.delete('/{category_name}', status_code=status.HTTP_200_OK, response_model=Message)
@admin_path
async def delete_category(user: cur_user_dependency, category_name: str, db: db_dependency):
    await CategoryCRUD.delete(category_name, db)
    return Message(message=f"Category {category_name} has been successfully deleted")


@router.post('/{category_name}/products/{product_id}', status_code=status.HTTP_200_OK, response_model=Message)
@admin_path
async def link_category_to_product(user: cur_user_dependency, category_name: str, product_id: int, db: db_dependency):
    if (category := await CategoryCRUD.get(category_name, db)) is None:
        raise ResourceDoesNotExistError("Category with the given name does not exist")
    if (product := await ProductCRUD.get(product_id, db)) is None:
        raise ResourceDoesNotExistError("Product with the given id does not exist")
    if category in product.categories:
        raise ResourceAlreadyExistsError(f"Product is already associated with the {category_name} category")
    category.products.append(product)
    return Message(message=f"Category {category_name} has been successfully linked to product with id {product_id}")


@router.get('/{category_name}/products', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def get_category_products(category_name: str, db: db_dependency):
    category = await CategoryCRUD.get(category_name, db)
    return category.products
