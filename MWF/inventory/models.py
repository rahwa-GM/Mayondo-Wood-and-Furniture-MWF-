from django.db import models
from django.core.validators import RegexValidator  # imports Django’s RegexValidator
from django.core.exceptions import ValidationError # imports Django’s ValidationError, which is used to raise errors when data fails validation
import datetime

# Create your models here.
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=15,
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
    address = models.TextField()

    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True) # Runs ONLY when the object is created
    updated_at = models.DateTimeField(auto_now=True) # Updates the field to the current date and time on every save()

    def clean(self):
        """
        Custom validation for Supplier.
    
        """

        if not self.name.strip():
            raise ValidationError({"name": "Supplier name cannot be empty or spaces."})
        
    def __str__(self):
        return self.name

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('Wood', 'Wood'),
        ('Furniture', 'Furniture')
    )

    name = models.CharField(max_length=50, unique=True)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    measurements = models.CharField(max_length=50, blank=True, null=True)

    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation for Product.

        """

        # filter(name__iexact=self.name) Find any product with EXACT same name but case-insensitive.
        # exclude(id=self.id) When editing an existing product, avoid checking against itself.
        # .exists() If such a product exists → True → raise error. 

        if not self.name.strip():
            raise ValidationError({"name": "Product name cannot be empty or spaces."})  
        
        if Product.objects.filter(name__iexact=self.name.strip()).exclude(id=self.id).exists():
            raise ValidationError({"name": "A product with this name already exists."})

        if not self.product_type:
            raise ValidationError({'product_type': "Please select a product type."})
       
        if self.color and not self.color.strip():
            raise ValidationError({"color": "Color cannot be empty spaces."})
        
        if self.measurements and not self.measurements.strip():
            raise ValidationError({"measurements": "Measurements cannot be empty spaces."})


        
    def __str__(self):
        return f"{self.name} ({self.product_type})"
    
class Stock(models.Model):
    # One Product can have many Stock entries 
    # If a product is deleted, all stock records also delete (CASCADE).
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # One Supplier can supply many Stock entries → One-to-Many
    # If a supplier is deleted, the stock record stays but the supplier becomes NULL
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    quality = models.CharField(max_length=30)
    date_received = models.DateField(blank=True, null=True)

    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Custom validation for Stock

        """

        if self.cost_price and self.cost_price <= 0:
            raise ValidationError({"cost_price": "Cost price must be greater than 0."}) 
        
        if self.product_price and self.product_price <= 0:
            raise ValidationError({"product_price": "Product price must be greater than 0."})
        
        if self.cost_price and self.product_price and self.product_price < self.cost_price:
            raise ValidationError({"product_price": "Selling price cannot be less than cost price."})
        
        if self.quality and self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than 0."})
        
        if not self.quality.strip():
            raise ValidationError({"quality": "Please enter the quality of the product."})
        
        if self.date_received and self.date_received > datetime.date.today():
            raise ValidationError({'date_received': "Date received cannot be in the future."})
        
        
    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"
    
    class Meta:
        ordering = ['-date_received']  # newest stocks first

    # read-only field
    @property
    def total_value(self):
        return self.cost_price * self.quantity
