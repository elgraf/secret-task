from django.forms import ModelForm, DateField, DateInput
from django.forms import ValidationError

from shop.settings import DATE_INPUT_FORMATS
from articles.models import (Category, Product, ProductPriceHistory,
                             CategoryPriceHistory)


class CategoryForm(ModelForm):
    btn_name = "Create"
    description = "Add new Category"

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
    btn_name = "Create"
    description = "Add new Product"

    @property
    def selfname(self):
        return type(self).__name__

    class Meta:
        model = Product
        fields = ('name', 'category', 'price')

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)


class PriceHystoryAbstractForm(ModelForm):
    pass


class ProductPriceHistoryForm(ModelForm):
    btn_name = "Change"
    description = "Change product price"

    @property
    def selfname(self):
        return type(self).__name__

    class Meta:
        model = ProductPriceHistory
        fields = ('product', 'start', 'end', 'modifier')

    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user', None)
        super(ProductPriceHistoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        inst = super(ProductPriceHistoryForm, self).save(commit=False)
        inst.user = self._user
        if inst.end and inst.start >= inst.end:
            raise ValidationError("Satart date is grater than end")
        if inst.modifier <= 0:
            raise ValidationError("Not allowed, modifier value must be > 0")
        if commit:
            inst.save()
            self.save_m2m()
        return inst


class CategoryPriceHistoryForm(ModelForm):
    btn_name = "Change"
    description = "Change cotegory price"

    class Meta:
        model = CategoryPriceHistory
        fields = ('category', 'start', 'end', 'modifier')

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
            raise ValidationError("Satart date is grater than end")
        if inst.modifier <= 0:
            raise ValidationError("Not allowed, modifier value must be > 0")
        if commit:
            inst.save()
            self.save_m2m()
        return inst
