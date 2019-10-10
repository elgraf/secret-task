import operator
from collections import namedtuple
from datetime import datetime as dt, date

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import (CASCADE, CharField, DateField, DateTimeField,
                              FloatField, ForeignKey, IntegerField, Manager,
                              ManyToManyField, Model, Q)

from articles.utils import chart_combination


class PriceHistory(Model):
    changed = DateTimeField(auto_now=True)
    user = ForeignKey(User, on_delete=CASCADE)
    start = DateField()
    end = DateField(default=dt.max.date())
    modifier = FloatField()

    objects = Manager()

    @staticmethod
    def _get_modifier_chart(history, stright=True
                            ) -> '[{"date": datetime.date, "m": float}, ]':
        if len(history) == 0:
            return [{"date": dt.min.date(), "m": 1},
                    {"date": dt.max.date(), "m": 1}]

        modifier = namedtuple('modifier', 'id start end modifier')
        price_hystory, start = [], None

        # Transform data from dict to named tuples
        # Add default modifier
        modifiers = tuple([modifier(*h.values()) for h in history] +
                          [modifier(0, dt.min.date(), dt.max.date(), 1.0)])

        start = min(modifiers, key=operator.itemgetter(1), default=None)
        current, current_date = start, start.start
        while current:
            price_hystory += [current]
            tmp = min(filter(
                lambda m: m.id > current.id and m.start >= current_date and
                m.start < current.end, modifiers),
                key=operator.itemgetter(1), default=None)
            if tmp:
                current = tmp
                current_date = tmp.start
            else:
                current_date = current.end
                current = next(filter(
                    lambda m: m.start < current.end and
                    m.end > current.end, modifiers), None)
        result = []
        prev = price_hystory[0]
        for ph in price_hystory[1:]:
            result += [dict(date=(prev.end if ph.id < prev.id else ph.start),
                            m=ph.modifier)]
            prev = ph

        if stright:
            for i in range(1, len(result)*2-1, 2):
                result.insert(
                    i, dict(date=result[i]["date"], m=result[i-1]["m"]))
            result += [dict(date=dt.max.date(), m=result[-1]["m"])]
        return result

    class Meta:
        abstract = True
        managed = False


class CategoryPriceHistory(PriceHistory):
    category = ForeignKey('Category', on_delete=CASCADE)

    objects = Manager()

    class Meta:
        abstract = False
        managed = True


class ProductPriceHistory(PriceHistory):
    product = ForeignKey('Product', on_delete=CASCADE)

    objects = Manager()

    class Meta:
        abstract = False
        managed = True


class Product(Model):
    name = CharField(max_length=255)
    category = ForeignKey('Category', on_delete=CASCADE)
    price = FloatField()

    objects = Manager()

    def __init__(self, *args, **kwargs):
        self._current_modifier = None
        self._unique_wishes = None
        super(Product, self).__init__(*args, **kwargs)

    def get_modifier_chart(self, start: 'date'=None, end: 'date'=None,
                           stright=True) -> '[(x=datetime.date, y=float)]':
        if start and start > end:
            return []
        start = start if start else dt.min.date()
        end = end if end else dt.max.date()
        # Get data from DB
        history = ProductPriceHistory.objects.filter(
            product=self, start__lte=end, end__gt=start).values(
            'id', 'start', 'end', 'modifier').order_by('-id')
        return PriceHistory._get_modifier_chart(
            history, stright=stright)

    def get_price_chart(self, start: 'date'=None, end: 'date'=None,
                        stright=True) -> '[(x=datetime.date, y=float)]':

        chart1 = self.get_modifier_chart(start=start, end=end, stright=False)
        chart2 = self.category.get_modifier_chart(
            start=start, end=end, stright=False)

        result = chart_combination(chart2, chart1)

        if stright:
            for i in range(1, len(result)*2-1, 2):
                result.insert(
                    i, dict(date=result[i]["date"], m=result[i-1]["m"]))
            result += [dict(date=dt.max.date(), m=result[-1]["m"])]
        for p in result:
            p["m"] *= self.price
        return result

    @property
    def price_hystory(self) -> '[ProductPriceHistory, ]':
        return ProductPriceHistory.objects.filter(product=self).all()

    @property
    def current_modifier(self) -> float:
        if self._current_modifier is None:
            current_date = dt.now().date()
            try:
                price_modifier_obj = ProductPriceHistory.objects.filter(
                    Q(product=self), Q(start__lte=current_date),
                    Q(end__gt=current_date) | Q(end=None)
                    ).order_by('-id').first()

                assert price_modifier_obj is not None
                self._current_modifier = price_modifier_obj.modifier
            except (ProductPriceHistory.DoesNotExist, AssertionError):
                self._current_modifier = 1.0

        return self._current_modifier

    @property
    def current_price(self) -> float:
        return round(self.price * self.current_modifier *
                     self.category.current_modifier, 2)

    @property
    def unique_wishes(self) -> int:
        """Return the number of unique additions to `WishList` per user"""
        if not self._unique_wishes:
            query = f"""SELECT count (DISTINCT wl.user_id)
                        FROM articles_wishedproduct AS wp
                        INNER JOIN articles_wishlist AS wl
                        ON wl.id = wp.wish_list_id
                        WHERE wp.product_id={self.id}
                    """
            with connection.cursor() as cursor:
                cursor.execute(query)
                self._unique_wishes = cursor.fetchone()[0]
        return self._unique_wishes

    def __str__(self):
        return self.name


class Category(Model):
    name = CharField(max_length=50, unique=True)

    objects = Manager()

    def __init__(self, *args, **kwargs):
        self._current_modifier = None
        super(Category, self).__init__(*args, **kwargs)

    def get_modifier_chart(self, start: 'date'=None, end: 'date'=None,
                           stright=True) -> '[(x=datetime.date, y=float)]':
        if start and start > end:
            return []
        start = start if start else dt.min.date()
        end = end if end else dt.max.date()
        # Get data from DB
        history = CategoryPriceHistory.objects.filter(
            category=self, start__lte=end, end__gt=start).values(
            'id', 'start', 'end', 'modifier').order_by('-id')

        return PriceHistory._get_modifier_chart(history, stright=stright)

    @property
    def price_hystory(self) -> [CategoryPriceHistory, ]:
        return CategoryPriceHistory.objects.filter(category=self).all()

    @property
    def current_modifier(self) -> float:
        if self._current_modifier is None:
            current_date = dt.now().date()
            try:
                price_modifier_obj = CategoryPriceHistory.objects.filter(
                    Q(category=self), Q(start__lte=current_date),
                    Q(end__gt=current_date) | Q(end=None)
                    ).order_by('-id').first()
                assert price_modifier_obj is not None
                self._current_modifier = price_modifier_obj.modifier
            except (CategoryPriceHistory.DoesNotExist, AssertionError):
                self._current_modifier = 1.0
        return self._current_modifier

    @property
    def get_all_products(self) -> [Product, ]:
        return Product.objects.filter(category=self).all()

    def __str__(self):
        return self.name


class WishList(Model):
    name = CharField(max_length=50)
    user = ForeignKey(User, on_delete=CASCADE)
    products = ManyToManyField(Product, through='WishedProduct')

    objects = Manager()

    class Meta:
        unique_together = ('name', 'user',)


class WishedProduct(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    wish_list = ForeignKey(WishList, on_delete=CASCADE)
    added_to = DateTimeField(auto_now_add=True)

    objects = Manager()

    class Meta:
        unique_together = ('wish_list', 'product',)
