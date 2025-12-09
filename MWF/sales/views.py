from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from .models import Customer, Sale
from staff.models import Staff
from .forms import CustomerForm, SaleForm
from decimal import Decimal
from django.utils.timezone import now
import csv
from django.http import HttpResponse

# Create your views here.

# ===========================
# CUSTOMER VIEWS
# ===========================

# Add Customer
@login_required
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully.")
            return redirect('sales:list_customer')
    else:
        form = CustomerForm()
    return render(request, 'sales/customer_form.html', {'form': form, 'title': 'Add Customer'})

# List Customers
@login_required
def list_customer(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'sales/customer_list.html', {'customers': customers})

# Update Customer
@login_required
def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect('sales:list_customer')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'sales/customer_update.html', {'form': form, 'customer': customer, 'title': 'Update Customer'})

# Delete Customer
@login_required
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect('sales:list_customer')
    return redirect('sales:list_customer')


# ===========================
# SALE VIEWS
# ===========================

# Add Sale
@login_required
def add_sale(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        if form.is_valid():
        # creates a Sale object but DOES NOT save it to the database yet. We delay saving because we must: calculate total price, update stock check availability first.
            sale = form.save(commit=False)

            stock_item = sale.stock_item # the product the customer is buying
  
            # Calculate Total Price
            total = sale.quantity * sale.price_per_unit # Calculates the base cost (without transport)

            if sale.provide_transport: # Checks whether the “Provide Transport” checkbox was selected
                total *= Decimal("1.05")  # Adds 5% transport cost

            sale.total_price = total # Saves the final calculated total into the sale object

            # Save Sale + Update Stock Safely
            with transaction.atomic(): # Ensures the following actions are ALL OR NOTHING: deduct stock save sale If anything fails, Django cancels everything
                if sale.transaction_type == "Sold":
                    # Check Stock Availability
                    # Checks if the user is trying to sell more than what's available
                    if sale.quantity > stock_item.quantity:
                        messages.error(request, f"Not enough stock! Available: {stock_item.quantity}.")
                        return render(request, "sales/sale_form.html", {"form": form, "title": "Add Sale"})
                    stock_item.quantity -= sale.quantity # Reduces the stock by quantity sold
                elif sale.transaction_type == "Bought":
                    stock_item.quantity += sale.quantity

                stock_item.save() # Saves the updated stock into the database.

                
                sale.save() # Finally saves the sale into the database

            messages.success(request, "Sale recorded successfully.") # Shows a success message after saving.
            return redirect("sales:list_sale") # Redirects the user to the sale list page

    else:
        form = SaleForm()

    return render(request, "sales/sale_form.html", {"form": form, "title": "Add Sale"})


# List Sales
@login_required
def list_sale(request):
    # select_related() fetches related foreign key objects in one query: product stock_item sold_by
    sales = Sale.objects.select_related('customer', 'product', 'stock_item', 'sold_by').order_by('-date_sold') # newest sales first
    return render(request, 'sales/sale_list.html', {'sales': sales})

# Update Sale
@login_required
def update_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk) # Fetch the sale from the database. If the sale does not exist → Django shows a 404 page.
    # original quantity BEFORE editing
    original_quantity = sale.quantity
    original_stock_item = sale.stock_item

    if request.method == "POST":
        form = SaleForm(request.POST, instance=sale) # Edit this existing sale instead of creating a new one
        if form.is_valid():
            updated_sale = form.save(commit=False) # Create updated sale object BUT do not save yet

            # Calculate total price
            total = updated_sale.quantity * updated_sale.price_per_unit            
            if updated_sale.provide_transport:
                total *= Decimal("1.05")
            updated_sale.total_price = total

            # Adjust stock (if quantity changed)
            # Calculate the difference: If positive: customer is buying more → reduce stock more If negative: customer is buying less → return stock
            stock_diff = updated_sale.quantity - original_quantity
            
            stock_item = updated_sale.stock_item
           
            # If user changed stock_item in form 
            # Prevent users from changing a sale from “Timber → Bed”
            if stock_item != original_stock_item:
                messages.error(request, "You cannot change the stock item of a sale.")
                return render(request, "sales/sale_update.html", {
                    'form': form, 
                    'sale': sale,
                    'title': 'Update Sale'
                })

         
           
            
            # Save Sale + Stock Safely
            with transaction.atomic(): # all changes happen OR none happen
                if updated_sale.transaction_type == "Sold":
                    # If quantity increased, check available stock
                    # If the user tries to sell more units than available → block operation.
                    if stock_diff > 0 and stock_diff > stock_item.quantity:                    
                        messages.error(request, f"Not enough stock! Available: {stock_item.quantity}.")
                        return render(request, "sales/sale_update.html", {
                        'form': form,
                        'sale': sale,
                        'title': 'Update Sale'
                })
                    # Update stock: reduce or increase
                    # If quantity increased → we subtract more
                    # If decreased → negative diff → subtraction becomes addition (returning stock)
                    stock_item.quantity -= stock_diff

                elif updated_sale.transaction_type == "Bought":
                    stock_item.quantity += stock_diff

                
                stock_item.save() # Save updated stock level

                updated_sale.save() # Save the updated sale to the database

            messages.success(request, "Sale updated successfully.")
            return redirect('sales:list_sale')
    else:
        form = SaleForm(instance=sale) # Pre-fill form with current sale information
    return render(request, 'sales/sale_update.html', {'form': form, 'sale': sale, 'title': 'Update Sale'})

# delete sale
@login_required
def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    stock_item = sale.stock_item

    if request.method == "POST":
        with transaction.atomic():
            if sale.transaction_type == "Sold": 
                # Return sold quantity back to stock
                stock_item.quantity += sale.quantity
            elif sale.transaction_type == "Bought":
                stock_item.quantity -= sale.quantity

            stock_item.save() # Save updated stock quantity

            sale.delete() # Delete the sale permanently

        messages.success(request, "Sale deleted and stock restored successfully.")
        return redirect('sales:list_sale')

    return redirect('sales:list_sale')
      

@login_required
def generate_sales_report(request):
    # Only managers can generate report
    staff = Staff.objects.filter(user=request.user).first()
    if not staff or staff.role != 'Manager':
        messages.error(request, 'Unauthorized access')
        return redirect('accounts:dashboard_agent')

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{now().date()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date Sold', 'Product', 'Quantity', 'Total Price', 'Sold By'])

    # Fetch all sold transactions
    sales = Sale.objects.filter(transaction_type='Sold').order_by('-date_sold')
    for s in sales:
        writer.writerow([s.date_sold, s.product.name, s.quantity, s.total_price, s.sold_by.user.username])

    return response