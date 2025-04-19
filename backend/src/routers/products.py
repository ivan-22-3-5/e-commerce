import uuid

from fastapi import APIRouter, status, Depends, UploadFile

from src.config import settings, rules
from src.crud import ProductCRUD, ReviewCRUD
from src.custom_exceptions import FileTooLargeError, NotSupportedFileTypeError, LimitExceededError, \
    ResourceDoesNotExistError
from src.db.models import Product
from src.deps import SessionDep, FileStorageDep
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


@router.get('/search', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def search_products(q: str, db: SessionDep):
    return await ProductCRUD.search(q, db)


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


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminRole])
async def delete_product(product_id: int, db: SessionDep):
    await ProductCRUD.delete(product_id, db)


# TODO: add resolution/aspect ratio regulation
@router.post('/{product_id}/images', status_code=status.HTTP_204_NO_CONTENT,
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

    if len(product.images) >= rules.MAX_IMAGES_PER_PRODUCT:
        raise LimitExceededError("Product already has the maximum number of images")

    ext = file.filename.split('.')[-1]
    file = await file.read()
    filename = f"{uuid.uuid4().hex}.{ext}"

    await storage.save(file, f"{product_id}/{filename}")
    # creating a new list is necessary for sqlalchemy to recognize the change
    product.images = product.images + [filename]


@router.put('/{product_id}/images', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminRole])
async def change_product_images(product_id: int, images: list[str], db: SessionDep, storage: FileStorageDep):
    product = await ProductCRUD.get(product_id, db)

    current_images = set(product.images)
    new_images = set(images)

    if not new_images.issubset(current_images):
        raise ResourceDoesNotExistError("One or more of the specified images does not exist")

    for filename in current_images - new_images:
        await storage.delete(f"{product_id}/{filename}")

    product.images = images


# region development postponed
@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: SessionDep):
    return await ReviewCRUD.get_by_product(product_id, db)
# endregion
