from fastapi import APIRouter, status, Depends

from src.crud import ProductCRUD, ReviewsCRUD
from src.db.models import Product
from src.deps import SessionDep
from src.permissions import AdminRole
from src.schemas.filtration import PaginationParams
from src.schemas.product import ProductIn, ProductOut, ProductUpdate
from src.schemas.review import ReviewOut

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def get_products(db: SessionDep, pagination: PaginationParams = Depends()):
    return await ProductCRUD.get_all(db=db, pagination=pagination, is_active=True)


@router.get('/all', status_code=status.HTTP_200_OK, response_model=list[ProductOut], dependencies=[AdminRole])
async def get_products_admin(db: SessionDep, pagination: PaginationParams = Depends(), is_active: bool = None):
    return await ProductCRUD.get_all(db=db, pagination=pagination, is_active=is_active)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ProductOut, dependencies=[AdminRole])
async def create_product(product: ProductIn, db: SessionDep):
    return await ProductCRUD.create(Product(
        **product.model_dump()
    ), db)


@router.patch('/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductOut, dependencies=[AdminRole])
async def update_product(product_id: int, product_update: ProductUpdate, db: SessionDep):
    return await ProductCRUD.update(product_id, product_update, db)


# region development postponed
@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: SessionDep):
    return await ReviewsCRUD.get_by_product(product_id, db)
# endregion
