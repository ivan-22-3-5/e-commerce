from fastapi import APIRouter, status, Depends

from src.crud import ProductCRUD, ReviewsCRUD
from src.db.models import Product
from src.deps import SessionDep, CurrentUserDep
from src.permissions import AdminRole
from src.schemas.filtration import PaginationParams
from src.schemas.product import ProductIn, ProductOut, ProductUpdate
from src.schemas.review import ReviewOut

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ProductOut,
             dependencies=[AdminRole])
async def create_product(product: ProductIn, db: SessionDep):
    return await ProductCRUD.create(Product(
        **product.model_dump()
    ), db)


@router.patch('/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductOut,
              dependencies=[AdminRole])
async def update_product(product_id: int, product_update: ProductUpdate, db: SessionDep):
    return await ProductCRUD.update(product_id, product_update, db)


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def get_products(user: CurrentUserDep, db: SessionDep,
                       pagination: PaginationParams = Depends(),
                       is_active: bool = None):
    if user.is_admin:
        return await ProductCRUD.get_all(db=db, pagination=pagination, is_active=is_active)
    return await ProductCRUD.get_all(db=db, pagination=pagination, is_active=True)


@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: SessionDep):
    return await ReviewsCRUD.get_by_product(product_id, db)
