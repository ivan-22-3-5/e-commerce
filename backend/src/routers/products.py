import uuid
from typing import Annotated

from fastapi import APIRouter, status, Depends, UploadFile, Query

from src.config import settings
from src.crud import ProductCRUD
from src.custom_exceptions import (
    FileTooLargeError,
    NotSupportedFileTypeError,
    ResourceDoesNotExistError
)
from src.deps import SessionDep, FileStorageDep, ProductServiceDep
from src.permissions import AdminRole
from src.schemas.filtration import PaginationParams
from src.schemas.product import ProductIn, ProductOut, ProductUpdate
from src.schemas.review import ReviewOut

router = APIRouter(
    prefix='/products',
    tags=['products']
)


@router.get('', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def get_products(product_service: ProductServiceDep, pagination: PaginationParams = Depends()):
    return await product_service.get_products(pagination=pagination, is_active=True)


@router.get('/search', status_code=status.HTTP_200_OK, response_model=list[ProductOut])
async def search_products(product_service: ProductServiceDep, q: str,
                          categories: Annotated[list[int], Query(alias="category")] = None,
                          pagination: PaginationParams = Depends()):
    return await product_service.search_products(q, categories=categories, pagination=pagination)


@router.get('/all', status_code=status.HTTP_200_OK, response_model=list[ProductOut], dependencies=[AdminRole])
async def get_products_admin(product_service: ProductServiceDep,
                             pagination: PaginationParams = Depends(),
                             is_active: bool = None):
    return await product_service.get_products(pagination=pagination, is_active=is_active)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=ProductOut, dependencies=[AdminRole])
async def create_product(product: ProductIn, product_service: ProductServiceDep):
    return await product_service.create_product(product)


@router.patch('/{product_id}', status_code=status.HTTP_200_OK, response_model=ProductOut, dependencies=[AdminRole])
async def update_product(product_id: int, product_update: ProductUpdate, product_service: ProductServiceDep):
    return await product_service.update_product(product_id, product_update)


@router.delete('/{product_id}', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminRole])
async def delete_product(product_id: int, product_service: ProductServiceDep):
    await product_service.delete_product(product_id)


# TODO: add resolution/aspect ratio regulation
@router.post('/{product_id}/images', status_code=status.HTTP_204_NO_CONTENT,
             dependencies=[AdminRole])
async def add_product_image(product_id: int, file: UploadFile, product_service: ProductServiceDep):
    # size check is performed when the file is ALREADY uploaded
    # this is wasteful, so the actual size regulation will be imposed on request by a proxy/middleware
    if file.size > settings.FILE_SIZE_LIMIT:
        raise FileTooLargeError("File is too large")
    if file.content_type not in settings.SUPPORTED_IMAGE_TYPES:
        raise NotSupportedFileTypeError("File type is not allowed")

    ext = file.filename.split('.')[-1]
    file = await file.read()
    filename = f"{uuid.uuid4().hex}.{ext}"

    await product_service.add_product_image(product_id, file, filename)


@router.put('/{product_id}/images', status_code=status.HTTP_204_NO_CONTENT, dependencies=[AdminRole])
async def change_product_images(product_id: int, images: list[str], product_service: ProductServiceDep):
    await product_service.change_product_images(product_id, images)


# region development postponed
@router.get('/{product_id}/reviews', status_code=status.HTTP_200_OK, response_model=list[ReviewOut])
async def get_product_reviews(product_id: int, db: SessionDep):
    return []
# endregion
