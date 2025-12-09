from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm

from staff.models import Staff # to check role
from sales.models import Sale
from inventory.models import Stock, Product
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncMonth
from django.utils.timezone import now
from datetime import datetime

# Create your views here.
def login_user(request):
    if request.method == "POST":
        # request the HttpRequest object (used for sessions, CSRF, etc.), Perform security checks
        # data=request.POST gives the form the typed username & password from the login page
        form = AuthenticationForm(request, data = request.POST)

        # triggers validation of the AuthenticationForm
        if form.is_valid(): 
            user = form.get_user() # get_user() retrieves the actual User object that matched the submitted credentials.
            login(request, user) # Django’s built-in function create a session and log them in
            
            # Staff.objects.filter(user=request.user) searches the Staff table for rows where: user == currently logged-in user
            # .filter().first() = get the Staff object if it exists, otherwise return None 
            staff = Staff.objects.filter(user = request.user).first() 

            # Check if staff profile exists
            if not staff:
                messages.error(request, 'Staff profile not found.')
                return redirect('accounts:login')


            # role-based redirection logic after login
            if staff.role == 'Manager':
                return redirect('accounts:dashboard_manager') # Managers go to "dashboard_manager"
            else:
                return redirect('accounts:dashboard_agent') # Agents go to "dashboard_agent"
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required # Only logged-in users can access the logout view
def logout_user(request):
    logout(request) # Clears the session, Logs out the user
    messages.success(request, 'Logged out successfully.') # Shows a friendly message on the login page after redirect.
    return redirect('accounts:login') # Takes the user back to the login screen

@login_required
def dashboard_manager(request):
    # Fetches the Staff object associated with the currently logged-in user.
    # .filter(...).first() is used so we get None if no staff exists instead of throwing an error.
    staff = Staff.objects.filter(user=request.user).first()
    # If there is no Staff profile, show an error and redirect to login.
    if not staff:
        messages.error(request, 'Staff profile not found.')
        return redirect('accounts:login')
    # Only managers can see this dashboard. Others (agents) get redirected to their dashboard.
    if staff.role != 'Manager':
        return redirect('accounts:dashboard_agent')

    # Total sales (sum of all sold transactions)
    # selects only the sold transactions.
    total_sales = Sale.objects.filter(transaction_type='Sold').aggregate(
        total=Sum('total_price') # sums up the total_price field across those transactions and stores it as 'total'
    )['total'] or 0 # If there are no sales, return 0 instead of None

    # Stock alerts (products with quantity <= 5)
    low_stock = Stock.objects.filter(quantity__lte=5).count() # selects all stock records with quantity less than or equal to 5
    out_of_stock = Stock.objects.filter(quantity=0).count()

    # Most sold product (by units)
    # .filter(transaction_type='Sold')
    # .values('product__name')
    # Count total units sold for each product
    most_sold_product = Sale.objects.filter(transaction_type='Sold') \
        .values('product__name') \
        .annotate(total_units=Sum('quantity')) \
        .order_by('-total_units').first() # Order by highest quantity
    most_sold_product_name = most_sold_product['product__name'] if most_sold_product else 'N/A'

    # Total staff
    total_staff = Staff.objects.count() # counts all staff in the database

    current_year = now().year # Get the current year
    # Create a list of all months (1-12)
    all_months = [datetime(current_year, m, 1) for m in range(1, 13)]
    month_labels = [m.strftime('%b') for m in all_months]  # Jan, Feb, ..., Dec
    
    # returns only the rows where: transaction_type = 'Sold' date_sold is in the current year
    # Group sales by month TruncMonth('date_sold') cuts the date to just the month. Example: 2025-03-14 → 2025-03-01 2025-03-27 → 2025-03-01 So all sales in March are grouped together.
    # Convert queryset to dictionary-like data
    # Django looks at all rows that belong to the same month and adds up their total_price
    monthly_sales_qs = Sale.objects.filter(transaction_type='Sold', date_sold__year=current_year) \
    .annotate(month=TruncMonth('date_sold')) \
    .values('month') \
    .annotate(total=Sum('total_price')) \
    .order_by('month') # Ensures data comes in this order: (Jan → Feb → Mar → ... → Dec)

    # range(1, 13) → numbers 1 to 12 (January to December)
    # datetime(current_year, m, 1) → creates a date representing the first day of each month. Result: [datetime(2025, 1, 1), datetime(2025, 2, 1), ..., datetime(2025, 12, 1)].
    monthly_sales_dict = {m['month'].strftime('%b'): float(m['total']) for m in monthly_sales_qs}# .strftime('%b') converts: 2025-01-01 → "Jan" 2025-02-01 → "Feb" total sales for that month (converted to float) Example: {'Dec': 120000.0} if you only have December data.
    sales_data = [monthly_sales_dict.get(m, 0) for m in month_labels] # Loops through all months (month_labels = Jan → Dec).get(m, 0) → if a month is missing in monthly_sales_dict, set value to 0
 
    # Top products sold (bar chart)
    # The double underscore product__name means: Go to the related Product object Get its name field instead of returning full Sale objects, we return grouped product names.
    # adds a new calculated field
    top_products = Sale.objects.filter(transaction_type='Sold') \
        .values('product__name') \
        .annotate(units_sold=Sum('quantity')) \
        .order_by('-units_sold')[:5] # Products with the most sales come first, the first 5 results only
    product_names = [p['product__name'] for p in top_products] # This loops through each dictionary and extracts the product name
    product_units = [p['units_sold'] for p in top_products] # This extracts the total units sold per product

    # Sales by category (pie chart)
    category_sales = Sale.objects.filter(transaction_type='Sold') \
        .values('product__product_type') \
        .annotate(total_units=Sum('quantity'))
    category_names = [c['product__product_type'] for c in category_sales] # extracts the category names into a simple list
    category_units = [c['total_units'] for c in category_sales] # extracts the units sold per category

    context = {
        "staff": staff,
        "months": month_labels,
        "sales_data": sales_data,
        "product_names": product_names,
        "product_units": product_units,
        "category_names": category_names,
        "category_sales": category_units,
        "total_sales": total_sales,
        "stock_alerts": low_stock,
        "out_of_stock": out_of_stock,
        "most_sold_product": most_sold_product_name,
        "total_staff": total_staff,
    }

    return render(request, 'accounts/dashboard_manager.html', context)

@login_required
def dashboard_agent(request):
    staff = Staff.objects.filter(user=request.user).first() # currently logged-in user (request.user)
    if not staff:
        messages.error(request, 'Staff profile not found.')
        return redirect('accounts:login')

    # Sales by this agent
    agent_sales_qs = Sale.objects.filter(sold_by=staff, transaction_type='Sold') # selects sales made by this particular staff member

    # Total sales
    agent_total_sales = agent_sales_qs.aggregate(total=Sum('total_price'))['total'] or 0

    # Top product
    # sums up the quantity of each product sold by this staff.
    top_product = agent_sales_qs.values('product__name') \
        .annotate(total_units=Sum('quantity')) \
        .order_by('-total_units').first() # sorts products by most units sold.
    agent_top_product = top_product['product__name'] if top_product else 'N/A' # If top_product exists, extract the product name. If no sales exist, fallback to 'N/A'.

    # Orders count & pending orders (assuming you have a 'status' field)
    agent_orders_count = agent_sales_qs.count() # all sales made by this staff member

    # Monthly sales (line chart)
    current_year = now().year
    # Create all months for the year creates ['Jan', 'Feb', 'Mar', ..., 'Dec']
    all_months = [datetime(current_year, m, 1) for m in range(1, 13)]
    agent_month_labels = [m.strftime('%b') for m in all_months]
    # Filters only sales made this year by the staff
    # truncates the date_sold field to the first day of the month.
    # Groups the queryset by month
    # Calculates total sales for each month
    monthly_sales_qs = agent_sales_qs.filter(date_sold__year=current_year) \
        .annotate(month=TruncMonth('date_sold')) \
        .values('month') \
        .annotate(total=Sum('total_price')) \
        .order_by('month') # Orders results from January → December

    # Loops through each dictionary in monthly_sales Converts the month date to a short month name (Jan, Feb, Mar…) using strftime('%b')
    # Convert queryset to dictionary: {"Jan": 200000, "Feb": 0, ...}
    monthly_dict = {m['month'].strftime('%b'): float(m['total']) for m in monthly_sales_qs}
    # Build final list with 0 for missing months
    agent_sales = [monthly_dict.get(m, 0) for m in agent_month_labels]


    # Top products sold (bar chart)
    # groups sales by product name
    # sums the quantity sold for each product
    top_products = agent_sales_qs.values('product__name') \
        .annotate(units_sold=Sum('quantity')) \
        .order_by('-units_sold')[:5] # sorts products from most sold → least sold takes only the top 5 products
    
    # Loops through each dictionary in top_products. Extracts product names into a list.
    agent_top_product_names = [p['product__name'] for p in top_products]
    # Loops through each dictionary in top_products. Extracts units sold for each product into a list
    agent_top_product_units = [p['units_sold'] for p in top_products]

    context = {
        "staff": staff,
        "agent_total_sales": agent_total_sales,
        "agent_top_product": agent_top_product,
        "agent_orders_count": agent_orders_count,
        "agent_months": agent_month_labels,
        "agent_sales": agent_sales,
        "agent_top_product_names": agent_top_product_names,
        "agent_top_product_units": agent_top_product_units,
    }

    return render(request, "accounts/dashboard_agent.html", context)

  




