from fastapi import APIRouter, status

from src.constraints import admin_path
from src.crud import ProductCRUD
from src.db.models import Product
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
    return await ProductCRUD.create(Product(
        **product.model_dump()
    ), db)


@router.patch('/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductOut)
@admin_path
async def update_product(user: cur_user_dependency, product_id: int, product_update: ProductUpdate, db: db_dependency):
    return await ProductCRUD.update(product_id, product_update, db)


@router.get('/all', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
@admin_path
async def get_all_products(user: cur_user_dependency, db: db_dependency):
    return await ProductCRUD.get_all(db=db)


@router.get('/inactive', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
@admin_path
async def get_inactive_products(user: cur_user_dependency, db: db_dependency):
    return await ProductCRUD.get_all(db=db, enabled=False)


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def get_active_products(db: db_dependency):
    return await ProductCRUD.get_all(db=db, enabled=True)


@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: db_dependency):
    product = await ProductCRUD.get(product_id, db)
    return product.reviews
