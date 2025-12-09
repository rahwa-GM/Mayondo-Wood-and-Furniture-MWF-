from django.db import models
from django.core.validators import RegexValidator  # imports Django’s RegexValidator
from django.core.exceptions import ValidationError # imports Django’s ValidationError, which is used to raise errors when data fails validation
from inventory.models import Product, Stock
from staff.models import Staff
from django.contrib.auth.models import User
import datetime

# Create your models here.
# inventory/models.py or sales/models.py
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        # adding validation rules to the field
        # validators=[ .. ]: A list of validation functions Django will run on this field
        # RegexValidator(...) A function that checks if the value matches a regular expression
        validators=[
            RegexValidator(
                regex=r"^\+?\d{9,15}$", # Only allow 9–15 digits, optional + at the start
                message="Phone number must be 9-15 digits, optionally starting with +" # Error message if validation fails

            )
        ]
    )    
    
    company = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True) # Runs ONLY when the object is created
    updated_at = models.DateTimeField(auto_now=True) # Updates the field to the current date and time on every save()


    def clean(self):
        """
        Custom validation for Product.

        """

        # filter(name__iexact=self.name) Find any customer with EXACT same name but case-insensitive.
        # exclude(id=self.id) When editing an existing custoer, avoid checking against itself.
        # .exists() If such a customer exists → True → raise error. 

        # Ensure name is not empty or whitespace
        if not self.name.strip():
            raise ValidationError({"name": "Customer name cannot be empty."})
        if Customer.objects.filter(name__iexact=self.name.strip()).exclude(id=self.id).exists():
            raise ValidationError({"name": "A customer with this name already exists."})
        
        
    
    def __str__(self):
        return self.name

class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Bank Overdraft', 'Bank Overdraft'),
    ]

    TRANSACTION_TYPES = [
        ('Sold', 'Sold'),
        ('Bought', 'Bought'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_item = models.ForeignKey(Stock, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES, default='Sold')  
    sold_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    date_sold = models.DateTimeField(auto_now_add=True)
    payment_type = models.CharField(max_length=15, choices=PAYMENT_CHOICES)
    provide_transport = models.BooleanField(default=False)  # calculate 5% in views

    created_at = models.DateTimeField(auto_now_add=True) # Runs ONLY when the object is created
    updated_at = models.DateTimeField(auto_now=True) # Updates the field to the current date and time on every save()


    def clean(self):
        # Quantity must be positive
        if self.quantity and self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})

        # Price per unit must be positive
        if self.price_per_unit and self.price_per_unit <= 0:
            raise ValidationError({"price_per_unit": "Price per unit must be greater than zero."})

        # # Total price should equal quantity * price_per_unit
        # if self.quantity and self.price_per_unit:
        #     expected_total = self.quantity * self.price_per_unit
        #     if self.total_price != expected_total:
        #         raise ValidationError({"total_price": f"Total price must equal quantity * price per unit ({expected_total})."})

        # Stock availability ONLY when selling
        if self.transaction_type == "Sold":
            if self.quantity:
                if self.stock_item.quantity < self.quantity:
                    raise ValidationError({"quantity": f"Not enough stock. Available: {self.stock_item.quantity}"})

        # Product matches stock item
        if self.product and self.stock_item:
            if self.product != self.stock_item.product:
                raise ValidationError({"product": "Selected product does not match the stock item."})

   

    def __str__(self):
        return f"Sale #{self.id} - {self.product.name} ({self.transaction_type})"

