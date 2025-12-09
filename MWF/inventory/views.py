from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required # imports the login_required decorator from Django’s authentication system.   
from django.contrib import messages
from .models import Supplier, Product, Stock
from staff.models import Staff
from .forms import SupplierForm, ProductForm, StockForm
import csv
from django.http import HttpResponse

# Create your views here.

# ===========================================================
# ADD SUPPLIER
# ===========================================================
@login_required
def add_supplier(request):
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier added successfully.")
            return redirect('inventory:list_suppplier')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupplierForm()
    
    return render(request, "inventory/supplier_form.html", {"form": form, "title": "Add Supplier"})

# ===========================================================
# LIST SUPPLIERS
# ===========================================================
@login_required
def list_supplier(request):
    suppliers = Supplier.objects.all().order_by("-created_at")  # newest first
    return render(request, "inventory/supplier_list.html", {"suppliers": suppliers})

# UPDATE SUPPLIER
# ===========================================================
@login_required
def update_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "Supplier updated successfully.")
            return redirect('inventory:list_supplier')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, "inventory/supplier_update.html", {"form": form, 'title': 'Update Supplier'})

# ===========================================================
# DELETE SUPPLIER
# ===========================================================
@login_required
def delete_supplier(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier.delete()
        messages.success(request, "Supplier deleted successfully.")
        return redirect('inventory:list_supplier')

    
    # If someone tries GET, just go back to list
    return redirect('inventory:list_supplier')

# ===========================================================
# ADD PRODUCT
# ===========================================================
@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully.")
            return redirect('inventory:list_product')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()

    return render(request, "inventory/product_form.html", {"form": form, 'title': 'Add Product'})

# ===========================================================
# LIST PRODUCTS
# ===========================================================
@login_required
def list_product(request):
    products = Product.objects.all().order_by("-created_at") # newest first
    return render(request, "inventory/product_list.html", {"products": products})

# ===========================================================
# UPDATE PRODUCT
# ===========================================================
@login_required
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('inventory:list_product')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ProductForm(instance=product)

    return render(request, "inventory/product_update.html", {"form": form,"product": product, 'title': 'Update Product'})

# ===========================================================
# DELETE PRODUCT
# ===========================================================
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect('inventory:list_product')

    return redirect('inventory:list_product')



# ===========================================================
# ADD STOCK
# ===========================================================
@login_required
def add_stock(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock added successfully.")
            return redirect('inventory:list_stock')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StockForm()

    return render(request, "inventory/stock_form.html", {"form": form, "title": "Add Stock"})

# ===========================================================
# LIST STOCK
# ===========================================================
@login_required
def list_stock(request):
    # Loads related product and supplier objects in the same database query
    # Sorts stock items by date_received (most recent first)
    stock_items = Stock.objects.select_related("product", "supplier").order_by("-date_received")
    return render(request, "inventory/stock_list.html", {"stock_items": stock_items})

# ===========================================================
# UPDATE STOCK
# ===========================================================
@login_required
def update_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)

    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, "Stock updated successfully.")
            return redirect('inventory:list_stock')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = StockForm(instance=stock)

    return render(request, "inventory/stock_update.html", {"form": form,"stock": stock,'title': 'Update Stock'})

# ===========================================================
# DELETE STOCK
# ===========================================================
@login_required
def delete_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)

    if request.method == "POST":
        stock.delete()
        messages.success(request, "Stock deleted successfully.")
        return redirect("inventory:list_stock")

    return redirect("inventory:list_stock")


@login_required
def generate_stock_report(request):
    # Only managers
    staff = Staff.objects.filter(user=request.user).first()
    if not staff or staff.role != 'Manager':
        messages.error(request, 'Unauthorized access')
        return redirect('accounts:dashboard_agent')

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="stock_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Product', 'Quantity', 'Cost Price', 'Selling Price', 'Date Received', 'Quality'])

    stocks = Stock.objects.all().order_by('product__name')
    for s in stocks:
        writer.writerow([
            s.product.name,
            s.quantity,
            s.cost_price,
            s.product_price,
            s.date_received,
            s.quality
        ])

    return response
