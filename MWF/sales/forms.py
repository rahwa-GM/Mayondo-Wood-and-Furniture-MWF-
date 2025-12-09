from django import forms
from .models import Customer, Sale
from inventory.models import Stock

# ===========================
# Customer Form
# ===========================
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone_number', 'company', 'address']
        error_messages = {
            'name': {
                'required': "Please enter the customer's name.",
                'max_length': "Name is too long."
            },
            'email': {
                'required': "Please enter an email address.",
                'invalid': "Enter a valid email address.",
                'unique': "A customer with this email already exists."
            },
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Customer name cannot be empty or whitespace.")
        if Customer.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("A customer with this name already exists.")
        return name
    
# ===========================
# Sale Form
# ===========================
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer', 'product', 'stock_item', 'quantity', 'price_per_unit', 'transaction_type', 'sold_by', 'payment_type', 'provide_transport']
        error_messages = {
            'quantity': {
                'required': "Please enter the quantity sold.",
                'min_value': "Quantity must be greater than zero.",
            },
            'price_per_unit': {
                'required': "Please enter the price per unit.",
                'min_value': "Price per unit must be greater than zero.",
            },
            'product': {
                'required': "Please select a product."
            },
            'stock_item': {
                'required': "Please select a stock item."
            },
            'sold_by': {
                'required': "Please select the staff who sold this item."
            }, 
            'payment_type': {
                'required': "Please select the type of payment."
            }
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None or quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_price_per_unit(self):
        price = self.cleaned_data.get('price_per_unit')
        if price is None or price <= 0:
            raise forms.ValidationError("Price per unit must be greater than zero.")
        return price

    def clean(self):
        cleaned_data = super().clean() # collects the cleaned values from all individual fields and returns a dictionary called cleaned_data.
        product = cleaned_data.get('product')
        stock_item = cleaned_data.get('stock_item')
        quantity = cleaned_data.get('quantity')

        if stock_item and quantity:
            # Check stock availability
            if stock_item.quantity < quantity:
                self.add_error('quantity', f"Not enough stock. Available: {stock_item.quantity}") # to attach errors to a specific field

            # Check that the stock_item matches the selected product
            if product and stock_item.product != product:
                self.add_error('stock_item', "Selected stock item does not match the product.")

        return cleaned_data
