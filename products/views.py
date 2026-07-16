from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import ProductForm, ProductSearchForm
from .models import Product, ProductImage


def product_list(request):
    form = ProductSearchForm(request.GET)
    queryset = (
        Product.objects.publicly_visible()
        .select_related("seller", "seller__profile")
        .prefetch_related("images")
    )
    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if form.cleaned_data.get("status"):
            queryset = queryset.filter(status=form.cleaned_data["status"])
        ordering = {
            "newest": ("-created_at", "-id"),
            "oldest": ("created_at", "id"),
            "price_asc": ("price", "id"),
            "price_desc": ("-price", "id"),
        }.get(form.cleaned_data.get("sort"), ("-created_at", "-id"))
        queryset = queryset.order_by(*ordering)
    page = Paginator(queryset, 12).get_page(request.GET.get("page"))
    return render(request, "products/product_list.html", {"form": form, "page": page})


def _visible_product_or_404(request, pk):
    product = get_object_or_404(
        Product.objects.select_related("seller", "seller__profile").prefetch_related("images"),
        pk=pk,
    )
    if product.visibility == Product.Visibility.PUBLIC and product.status not in {
        Product.Status.BLOCKED,
        Product.Status.DELETED,
        Product.Status.DRAFT,
    }:
        return product
    if request.user.is_authenticated and (request.user == product.seller or request.user.is_staff):
        return product
    raise Http404


def product_detail(request, pk):
    return render(
        request, "products/product_detail.html", {"product": _visible_product_or_404(request, pk)}
    )


@login_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        product.save()
        if form.cleaned_data.get("image"):
            ProductImage.objects.create(
                product=product, image=form.cleaned_data["image"], alt_text=product.title
            )
        return redirect("products:detail", pk=product.pk)
    return render(request, "products/product_form.html", {"form": form, "heading": "상품 등록"})


def _owned_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.seller_id != request.user.id:
        raise PermissionDenied
    if product.status == Product.Status.BLOCKED:
        raise PermissionDenied
    return product


@login_required
def product_update(request, pk):
    product = _owned_product(request, pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        if form.cleaned_data.get("image"):
            ProductImage.objects.create(
                product=product, image=form.cleaned_data["image"], alt_text=product.title
            )
        return redirect("products:detail", pk=product.pk)
    return render(
        request,
        "products/product_form.html",
        {"form": form, "heading": "상품 수정", "product": product},
    )


@login_required
@require_POST
def product_delete(request, pk):
    product = _owned_product(request, pk)
    product.status = Product.Status.DELETED
    product.deleted_at = timezone.now()
    product.save(update_fields=("status", "deleted_at", "updated_at"))
    return redirect("products:mine")


@login_required
def my_products(request):
    products = (
        Product.objects.filter(seller=request.user)
        .exclude(status=Product.Status.DELETED)
        .prefetch_related("images")
    )
    return render(request, "products/my_products.html", {"products": products})
