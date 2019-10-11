
from items.forms import (
    ProductPriceHistoryForm,
    CategoryPriceHistoryForm,
    CategoryForm,
    ProductForm
)


def navbarforms(request):
    return {
        "forms": [
            CategoryForm(),
            ProductForm(),
            ProductPriceHistoryForm(),
            CategoryPriceHistoryForm(),
        ],
    }
