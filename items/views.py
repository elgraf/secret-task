import json

from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import (
    Http404,
    HttpResponseRedirect,
    JsonResponse,
    HttpResponseBadRequest
)
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from items.forms import (
    CategoryForm,
    CategoryPriceHistoryForm,
    ProductForm,
    ProductPriceHistoryForm,
)
from items.models import (
    Category,
    CategoryPriceHistory,
    Product,
    ProductPriceHistory
)


class CategoryView(View):
    template = "categories.html"

    @method_decorator(login_required)
    def get(self, request):
        context = {
            "categories": Category.objects.all(),
        }
        return render(request, self.template, context=context)

    @method_decorator(login_required)
    def post(self, request):
        form_class = globals()[request.POST["save_form"]]
        form = form_class(request.POST, user=request.user)

        if form.is_valid():
            try:
                form.save()
            except ValidationError as e:
                return HttpResponseBadRequest(f"ValidationError ERROR:{e}")

        return HttpResponseRedirect(request.path_info)


class ItemsView(View):
    template = "items.html"

    @method_decorator(login_required)
    def get(self, request, category):
        try:
            category = Category.objects.get(name=category)
        except Category.DoesNotExist:
            raise Http404()

        context = {
            "products": category.get_all_products
        }

        return render(request, self.template, context=context)


class CategoryChartView(View):
    template = "chart.html"

    @method_decorator(login_required)
    def get(self, request, category):
        if category == "...":
            raise Http404()
        try:
            category = Category.objects.get(name=category)
        except Category.DoesNotExist:
            raise Http404()

        category_chart = [{"date": str(d["date"]), "m": d["m"]} for d in
                          category.get_alterated_chart_history()]
        context = {
            "chart": json.dumps({
                "chart": category_chart
            }),
        }

        return render(request, self.template, context=context)


class ItemsChartView(View):
    template = "chart.html"

    @method_decorator(login_required)
    def get(self, request, product_id, **kwargs):
        try:
            product = Product.objects.get(id=product_id)
        except Category.DoesNotExist:
            raise Http404()

        context = {
            "chart": json.dumps({
                "chart": [{"date": str(d["date"]), "m": d["m"]} for d in
                          product.get_price_chart()]
            }),
        }

        return render(request, self.template, context=context)
