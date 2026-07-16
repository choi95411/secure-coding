from django import forms

from .models import Product
from .validators import validate_product_image


class ProductForm(forms.ModelForm):
    image = forms.ImageField(
        required=False, validators=[validate_product_image], label="상품 이미지"
    )

    class Meta:
        model = Product
        fields = ("title", "description", "price", "status", "visibility")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}

    def clean_status(self):
        status = self.cleaned_data["status"]
        if status in {Product.Status.BLOCKED, Product.Status.DELETED}:
            raise forms.ValidationError("사용자가 선택할 수 없는 상태입니다.")
        return status


class ProductSearchForm(forms.Form):
    q = forms.CharField(required=False, max_length=100, label="검색어")
    status = forms.ChoiceField(
        required=False,
        choices=[
            ("", "전체 상태"),
            (Product.Status.AVAILABLE, "판매 중"),
            (Product.Status.RESERVED, "예약 중"),
            (Product.Status.SOLD, "판매 완료"),
        ],
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ("newest", "최신순"),
            ("oldest", "오래된순"),
            ("price_asc", "낮은 가격순"),
            ("price_desc", "높은 가격순"),
        ],
    )
