import operator

from collections import namedtuple
from datetime import datetime as dt, date


from django.contrib.auth.models import User
from django.db.models import (
    CASCADE,
    CharField,
    DateField,
    DateTimeField,
    FloatField,
    ForeignKey,
    Manager,
    Model,
    Q
)

from items.utils import chart_slice


class PriceHistory(Model):
    changed = DateTimeField(auto_now=True)
    user = ForeignKey(User, on_delete=CASCADE)
    start = DateField()
    end = DateField(default=dt.max.date())
    alter = FloatField()

    @staticmethod
    def _get_alterated_chart_history(history, stright=True
                                     ) -> '[{"date": datetime.date, "m": float}, ]':
        if len(history) == 0:
            return [{"date": dt.min.date(), "m": 1},
                    {"date": dt.max.date(), "m": 1}]

        offset = namedtuple('offset', 'id start end value')
        price_history, start = [], None

        # Transform data from dict to named tuples
        # Add default alter value
        offsets = tuple([offset(*h.values()) for h in history] +
                        [offset(0, dt.min.date(), dt.max.date(), 1.0)])

        start = min(offsets, key=operator.itemgetter(1), default=None)
        current, current_date = start, start.start
        while current:
            price_history += [current]
            tmp = min(filter(
                lambda m: m.id > current.id and current_date <= m.start < current.end, offsets),
                key=operator.itemgetter(1), default=None)
            if tmp:
                current = tmp
                current_date = tmp.start
            else:
                current_date = current.end
                current = next(filter(
                    lambda m: m.start < current.end < m.end, offsets), None)
        result = []
        prev = price_history[0]
        for ph in price_history[1:]:
            result += [dict(date=(prev.end if ph.id < prev.id else ph.start),
                            m=ph.value)]
            prev = ph

        if stright:
            for i in range(1, len(result) * 2 - 1, 2):
                result.insert(
                    i, dict(date=result[i]["date"], m=result[i - 1]["m"]))
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

    class Meta:
        abstract = False
        managed = True


class Product(Model):
    name = CharField(max_length=255)
    category = ForeignKey('Category', on_delete=CASCADE)
    price = FloatField()

    objects = Manager()

    def __init__(self, *args, **kwargs):
        self._current_alter_value = None
        super(Product, self).__init__(*args, **kwargs)

    def get_alterated_chart_history(self, start: 'date' = None, end: 'date' = None,
                                    stright=True) -> '[(x=datetime.date, y=float)]':
        if start and start > end:
            return []
        start = start if start else dt.min.date()
        end = end if end else dt.max.date()
        # Get data from DB
        history = ProductPriceHistory.objects.filter(
            product=self, start__lte=end, end__gt=start).values(
            'id', 'start', 'end', 'alter').order_by('-id')
        return PriceHistory._get_alterated_chart_history(
            history, stright=stright)

    def get_price_chart(self, start: 'date' = None, end: 'date' = None,
                        stright=True) -> '[(x=datetime.date, y=float)]':

        chart1 = self.get_alterated_chart_history(start=start, end=end, stright=False)
        chart2 = self.category.get_alterated_chart_history(
            start=start, end=end, stright=False)

        result = chart_slice(chart2, chart1)

        if stright:
            for i in range(1, len(result) * 2 - 1, 2):
                result.insert(
                    i, dict(date=result[i]["date"], m=result[i - 1]["m"]))
            result += [dict(date=dt.max.date(), m=result[-1]["m"])]
        for p in result:
            p["m"] += self.price
        return result

    @property
    def price_history(self) -> '[ProductPriceHistory, ]':
        return ProductPriceHistory.objects.filter(product=self).all()

    @property
    def current_alter_value(self) -> float:
        if self._current_alter_value is None:
            current_date = dt.now().date()
            try:
                price_alter_obj = ProductPriceHistory.objects.filter(
                    Q(product=self), Q(start__lte=current_date),
                    Q(end__gt=current_date) | Q(end=None)
                ).order_by('-id').first()

                assert price_alter_obj is not None
                self._current_alter_value = price_alter_obj.alter
            except (ProductPriceHistory.DoesNotExist, AssertionError):
                self._current_alter_value = 0.0

        return self._current_alter_value

    @property
    def current_price(self) -> float:
        return round(self.price + self.current_alter_value +
                     self.category.current_alter_value, 2)

    def __str__(self):
        return self.name


class Category(Model):
    name = CharField(max_length=50, unique=True)

    def __init__(self, *args, **kwargs):
        self._current_alter_value = None
        super(Category, self).__init__(*args, **kwargs)

    def get_alterated_chart_history(self, start: 'date' = None, end: 'date' = None,
                           stright=True) -> '[(x=datetime.date, y=float)]':
        if start and start > end:
            return []
        start = start if start else dt.min.date()
        end = end if end else dt.max.date()
        # Get data from DB
        history = CategoryPriceHistory.objects.filter(
            category=self, start__lte=end, end__gt=start).values(
            'id', 'start', 'end', 'alter').order_by('-id')

        return PriceHistory._get_alterated_chart_history(history, stright=stright)

    @property
    def price_history(self) -> [CategoryPriceHistory, ]:
        return CategoryPriceHistory.objects.filter(category=self).all()

    @property
    def current_alter_value(self) -> float:
        if self._current_alter_value is None:
            current_date = dt.now().date()
            try:
                price_alter_obj = CategoryPriceHistory.objects.filter(
                    Q(category=self), Q(start__lte=current_date),
                    Q(end__gt=current_date) | Q(end=None)
                ).order_by('-id').first()
                assert price_alter_obj is not None
                self._current_alter_value = price_alter_obj.alter
            except (CategoryPriceHistory.DoesNotExist, AssertionError):
                self._current_alter_value = 0.0
        return self._current_alter_value

    @property
    def get_all_products(self) -> [Product, ]:
        return Product.objects.filter(category=self).all()

    def __str__(self):
        return self.name
