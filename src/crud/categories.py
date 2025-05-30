from src.crud.base import Retrievable, Deletable, Creatable
from src.db import models


class CategoryCRUD(Creatable, Retrievable, Deletable):
    model = models.Category
    key = models.Category.id
