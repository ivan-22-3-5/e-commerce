import uuid

from fastapi import APIRouter, status, Depends, UploadFile

from src.config import settings
from src.crud import ProductCRUD, ReviewCRUD, ProductImageCRUD
from src.custom_exceptions import FileTooLargeError, NotSupportedFileTypeError, LimitExceededError
from src.db.models import Product, ProductImage
from src.deps import SessionDep, FileStorageDep
from src.permissions import AdminRole
from src.schemas.filtration import PaginationParams
from src.schemas.image import ProductImageOut
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


# TODO: add resolution/aspect ratio regulation
@router.post('/{product_id}/images', status_code=status.HTTP_201_CREATED, response_model=ProductImageOut,
             dependencies=[AdminRole])
async def add_product_image(product_id: int, file: UploadFile,
                            db: SessionDep, storage: FileStorageDep):
    # size check is performed when the file is ALREADY uploaded
    # this is wasteful, so the actual size regulation will be imposed on request by a proxy/middleware
    if file.size > settings.FILE_SIZE_LIMIT:
        raise FileTooLargeError("File is too large")
    if file.content_type not in settings.SUPPORTED_IMAGE_TYPES:
        raise NotSupportedFileTypeError("File type is not allowed")

    product = await ProductCRUD.get(product_id, db)

    if len(product.images) >= settings.MAX_IMAGES_PER_PRODUCT:
        raise LimitExceededError("Product already has the maximum number of images")

    ext = file.filename.split('.')[-1]
    file = await file.read()
    uri = f"{product_id}/{uuid.uuid4().hex}.{ext}"

    await storage.save(file, uri)
    return await ProductImageCRUD.create(ProductImage(
        product_id=product_id,
        uri=uri,
        is_primary=len(product.images) == 0
    ), db)


# region development postponed
@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: SessionDep):
    return await ReviewCRUD.get_by_product(product_id, db)
# endregion
