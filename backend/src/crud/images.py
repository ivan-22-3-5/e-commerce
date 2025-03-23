from src.crud.base import Deletable, Creatable
from src.db import models


class ProductImageCRUD(Creatable, Deletable):
    model = models.ProductImage
    key = models.ProductImage.id
    not_found_message = "Product image with the given id does not exist"
