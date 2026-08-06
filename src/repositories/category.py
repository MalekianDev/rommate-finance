from db.models import Category
from repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """
    Repository for category-related operations.
    """

    model = Category
