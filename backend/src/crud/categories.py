from src.crud.base import Retrievable, Deletable, Creatable
from src.db import models


class CategoryCRUD(Creatable, Retrievable, Deletable):
    model = models.Category
    key = models.Category.id
    not_found_message = "Category with the given id does not exist"
