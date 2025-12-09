from django import forms
from .models import Supplier, Product, Stock
from django.core.exceptions import ValidationError
import datetime


# ===========================================================
# SUPPLIER FORM
# ===========================================================
class SupplierForm(forms.ModelForm):

    class Meta:
        model = Supplier
        fields = "__all__"

        error_messages = {
            "name": {
                "required": "Please enter the supplier name.",
                "max_length": "Name cannot exceed 100 characters.",
            },
            "email": {
                "required": "Please enter an email address.",
                "invalid": "Please enter a valid email format.",
                "unique": "A supplier with this email already exists.",
            },
            "phone_number": {
                "required": "Phone number is required.",
                "invalid": "Phone number must be 9–15 digits and may start with +.",
            },
        }

        # Form field customizations
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Supplier Name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "example@domain.com"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+256700000000"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    # Additional form-specific validation
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name.strip():
            raise ValidationError("Supplier name cannot be empty or spaces.")
        return name


# ===========================================================
# PRODUCT FORM
# ===========================================================
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

        error_messages = {
            "name": {
                "required": "Product name is required.",
                "max_length": "Product name cannot exceed 50 characters.",
            },
            "product_type": {
                "required": "Please select a product type.",
            },
        }

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Product Name"}),
            "product_type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "color": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "measurements": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
        }

    # Custom field validation: name
    def clean_name(self):
        name = self.cleaned_data.get("name")

        if not name.strip():
            raise ValidationError("Product name cannot be only spaces.")

        # Case-insensitive unique name validation
        if Product.objects.filter(name__iexact=name.strip()).exclude(id=self.instance.id).exists():
            raise ValidationError("A product with this name already exists.")

        return name

    # Validate color (optional but cannot be only spaces)
    def clean_color(self):
        color = self.cleaned_data.get("color")
        if color and not color.strip():
            raise ValidationError("Color cannot be empty spaces.")
        return color

    # Validate measurements
    def clean_measurements(self):
        measurements = self.cleaned_data.get("measurements")
        if measurements and not measurements.strip():
            raise ValidationError("Measurements cannot be empty spaces.")
        return measurements

# ===========================================================
# STOCK FORM
# ===========================================================
class StockForm(forms.ModelForm):

    class Meta:
        model = Stock
        fields = "__all__"

        error_messages = {
            "cost_price": {
                "required": "Cost price is required.",
                "invalid": "Please enter a valid number.", # non-numeric or badly formatted input
            },
            "product_price": {
                "required": "Selling price is required.",
                "invalid": "Please enter a valid number.", 
            },
            "quantity": {
                "required": "Quantity is required.",
                "invalid": "Quantity must be a whole number.",
            },
            "quality": {
                "required": "Please specify the quality.",
            },
        }

        widgets = {
            "product": forms.Select(attrs={"class": "form-control"}),
            "supplier": forms.Select(attrs={"class": "form-control"}),
            "cost_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}), # Users can only enter values like 1.00, 1.25, 2.50, etc.
            "product_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1", "step": "1"}), # step="1" ensures the user can only increase/decrease in whole numbers.
            "quality": forms.TextInput(attrs={"class": "form-control"}),
            "date_received": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    # Custom validation: cost_price
    def clean_cost_price(self):
        cost = self.cleaned_data.get("cost_price")
        if cost <= 0:
            raise ValidationError("Cost price must be greater than 0.")
        return cost

    # Custom validation: product_price
    def clean_product_price(self):
        price = self.cleaned_data["product_price"]
        cost = self.cleaned_data.get("cost_price")  # Use get to avoid crash if cost failed validation
        if price <= 0:
            raise ValidationError("Selling price must be greater than 0.")
        if cost is not None and price < cost:
            raise ValidationError("Selling price cannot be less than cost price.")
        return price


    # Custom validation: quantity
    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty <= 0:
            raise ValidationError("Quantity must be greater than 0.")
        return qty

    # Custom validation: quality
    def clean_quality(self):
        quality = self.cleaned_data.get("quality")
        if not quality.strip():
            raise ValidationError("Please enter the product quality.")
        return quality

    # Custom validation: date_received
    def clean_date_received(self):
        date_received = self.cleaned_data.get("date_received")

        if date_received and date_received > datetime.date.today():
            raise ValidationError("Date received cannot be in the future.")

        return date_received