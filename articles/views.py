import json
from datetime import datetime as dt

from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.forms import ValidationError
from django.http import (Http404, HttpResponseRedirect, JsonResponse,
                         HttpResponseBadRequest)
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from articles.forms import (CategoryForm, CategoryPriceHistoryForm,
                            ProductForm, ProductPriceHistoryForm, )
from articles.models import (Category, CategoryPriceHistory, Product,
                             ProductPriceHistory, WishedProduct, WishList)


class CategoryView(View):
    template = "categories.html"

    @method_decorator(login_required)
    def get(self, request):
        category = Category.objects.filter(id__gte=1).all()
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


class ProductsView(View):
    template = "products.html"

    @method_decorator(login_required)
    def get(self, request, category):
        if category == "...":
            raise Http404()
        try:
            category = Category.objects.get(name=category)
        except Category.DoesNotExist:
            raise Http404()

        context = {
            "products": category.get_all_products,
            "wish_lists": WishList.objects.filter(user=request.user).all()
        }

        return render(request, self.template, context=context)

    @method_decorator(login_required)
    def post(self, request, category):
        response, status = "Invalid or not defined action", 403
        if request.POST["action"] == "new_wish_list":
            name = request.POST["name"]
            if len(name) > 3:
                try:
                    new_wish_list = WishList.objects.create(
                        name=name,
                        user=request.user
                    )
                    response, status = new_wish_list.id, 200
                except IntegrityError:
                    response, status = "List with same name alredy exists", 412
            else:
                response, status = "Whish list name must be > 3", 412
        elif request.POST["action"] == "add_prod_to_wl":
            try:
                WishedProduct.objects.update_or_create(
                    product_id=int(request.POST["product_id"]),
                    wish_list_id=int(request.POST["wish_list_id"]),
                    defaults={"added_to": dt.now()}
                )
                response, status = None, 200
            except ValueError:
                response, status = "Data validation error", 412

        return JsonResponse({"result": response}, status=status)


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
                          category.get_modifier_chart()]
        context = {
            "chart": json.dumps({
                "chart": category_chart
            }),
        }

        return render(request, self.template, context=context)


class ProductChartView(View):
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
