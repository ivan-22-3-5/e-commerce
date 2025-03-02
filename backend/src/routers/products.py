from fastapi import APIRouter, status

from src.constraints import admin_path
from src.crud import products
from src.custom_exceptions import ResourceDoesNotExistError
from src.deps import db_dependency, cur_user_dependency
from src.schemas.product import ProductIn, ProductOut, ProductUpdate
from src.schemas.review import ReviewOut

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ProductOut)
@admin_path
async def create_product(user: cur_user_dependency, product: ProductIn, db: db_dependency):
    return await products.create(product, db)


@router.patch('/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductOut)
@admin_path
async def update_product(user: cur_user_dependency, product_id: int, product_update: ProductUpdate, db: db_dependency):
    return await products.update(product_id, product_update, db)


@router.get('/all', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
@admin_path
async def get_all_products(user: cur_user_dependency, db: db_dependency):
    return await products.get_all(db=db)


@router.get('/inactive', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
@admin_path
async def get_inactive_products(user: cur_user_dependency, db: db_dependency):
    return await products.get_all(db=db, enabled=False)


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def get_active_products(db: db_dependency):
    return await products.get_all(db=db, enabled=True)


@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: db_dependency):
    if (product := await products.get_by_id(product_id, db)) is None:
        raise ResourceDoesNotExistError("Product with the given id does not exist")
    return product.reviews
