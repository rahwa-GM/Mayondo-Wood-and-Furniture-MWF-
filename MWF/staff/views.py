from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # imports the login_required decorator from Django’s authentication system.   
from .models import Staff # The dot (.) means from the current app, import the model named Staff.
from .forms import StaffForm # Importing from the forms.py file in the same app
from django.contrib import messages # Import Django's messaging framework to display one-time notifications to users


# Create your views here.
# ----------------------------------------------------------------
# List all staff members
# ----------------------------------------------------------------

@login_required
def list_staff(request):
    staff = Staff.objects.all() # to retrieve all records from the Staff model
    return render(request, 'staff/staff_list.html', {'staff' : staff})

# ----------------------------------------------------------------
# Create a new staff member
# ----------------------------------------------------------------
@login_required
def add_staff(request):
    if request.method == 'POST': # User submitted the form
        # create a form object filled with user’s submitted values
        # request.POST contains all form input values
        form = StaffForm(request.POST) 
        if form.is_valid(): # Check if the values are valid
            form.save() # Save the data to the database if valid, Display the form back with errors if invalid
            return redirect('staff_list') # Redirect user to staff listing page after successful submission
    else:
        form = StaffForm() # If it's a GET request → show empty form
    return render(request, 'staff/staff_form.html', {'form': form}) # passing the form object to the template

# ----------------------------------------------------------------
# Update an existing staff member
# ----------------------------------------------------------------
@login_required
def update_staff(request, pk):
    # get_object_or_404: fetch a single object or automatically show a 404 page if it’s not found.
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        # tells Django you are updating an existing object with the submitted data instead of creating a new one.
        form = StaffForm(request.POST, instance=staff) 
        if form.is_valid():
            form.save() # updates existing object
            messages.success(request, 'Staff profile updated successfully.')
            return redirect('staff_list')

    else:
        # instance=staff tells Django: “This form is bound to this specific Staff object from the database.
        form = StaffForm(instance=staff) # Create a form pre-filled with the staff's current data allows the user to see existing data.

    # Render the form template
    return render(request, 'staff/staff_form.html', {'form': form})

# ----------------------------------------------------------------
# Delete a staff member
# ----------------------------------------------------------------
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()  # Delete the object
        # Add a one-time success message that will be displayed to the user after deletion
        messages.success(request, 'Staff profile deleted successfully.')
        return redirect('staff_list') # Redirect to the list page after deletion
    # If not POST, render a confirmation template
    return render(request, 'staff/staff_form.html', {'staff': staff}) 