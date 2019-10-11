from django.forms import ModelForm
from django.forms import ValidationError


from items.models import (
    Category,
    Product,
    ProductPriceHistory,
    CategoryPriceHistory
)


class CategoryForm(ModelForm):
    btn_name = "Add"
    description = "Add new category"

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super(CategoryForm, self).__init__(*args, **kwargs)

    @property
    def selfname(self):
        return type(self).__name__

    class Meta:
        model = Category
        fields = ('name',)


class ProductForm(ModelForm):
    btn_name = "Add"
    description = "Add new product"

    @property
    def selfname(self):
        return type(self).__name__

    class Meta:
        model = Product
        fields = ('name', 'category', 'price')

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)


class ProductPriceHistoryForm(ModelForm):
    btn_name = "Modify"
    description = "Modify product price"

    @property
    def selfname(self):
        return type(self).__name__

    class Meta:
        model = ProductPriceHistory
        fields = ('product', 'start', 'end', 'alter')

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super(ProductPriceHistoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super(ProductPriceHistoryForm, self).save(commit=False)
        inst.user = self._user
        if inst.end and inst.start >= inst.end:
            raise ValidationError("Start date is greater than end date.")
        if commit:
            inst.save()
            self.save_m2m()
        return inst


class CategoryPriceHistoryForm(ModelForm):
    btn_name = "Modify"
    description = "Modify category price"

    class Meta:
        model = CategoryPriceHistory
        fields = ('category', 'start', 'end', 'alter')

    @property
    def selfname(self):
        return type(self).__name__

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super(CategoryPriceHistoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super(CategoryPriceHistoryForm, self).save(commit=False)
        inst.user = self._user
        if inst.end and inst.start >= inst.end:
            raise ValidationError("Start date is greater than end date.")
        if commit:
            inst.save()
            self.save_m2m()
        return inst
