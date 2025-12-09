from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required # imports the login_required decorator from Django’s authentication system.   
from .models import Staff # The dot (.) means from the current app, import the model named Staff.
from .forms import StaffForm, UserForm, StaffUserForm # Importing from the forms.py file in the same app
from django.contrib import messages # Import Django's messaging framework to display one-time notifications to users


# Create your views here.
# ----------------------------------------------------------------
# List all staff members
# ----------------------------------------------------------------

# @login_required
def list_staff(request):
    logged_in_staff = Staff.objects.filter(user = request.user).first() # logged-in staff
    # All Staff objects and their related User objects are fetched in one go
    # 'user' in select_related('user') tells Django: “When fetching Staff, also fetch the related User in the same query.
    staff_members = Staff.objects.select_related('user').all() 
    return render(request, 'staff/staff_list.html', {
                'staff' : logged_in_staff,   # for sidebar
                'staff_members': staff_members })

# ----------------------------------------------------------------
# Create a new staff member
# ----------------------------------------------------------------
# @login_required
def add_staff(request):
    if request.method == 'POST': # User submitted the form
        # create a form object filled with user’s submitted values
        # request.POST contains all form input values
        form = StaffUserForm(request.POST) 
        if form.is_valid(): # Check if the values are valid
            form.save() # Save the data to the database if valid, Display the form back with errors if invalid
            return redirect('staff:list') # Redirect user to staff listing page after successful submission
    else:
        form = StaffUserForm() # If it's a GET request → show empty form
    return render(request, 'staff/staff_form.html', {'form': form, "title": "Add Staff"}) # passing the form object to the template

# ----------------------------------------------------------------
# Update an existing staff member
# ----------------------------------------------------------------
# @login_required
def update_staff(request, pk):
    # get_object_or_404: fetch a single object or automatically show a 404 page if it’s not found.
    staff = get_object_or_404(Staff, pk=pk)
    user = staff.user

    if request.method == 'POST':
        # tells Django you are updating an existing object with the submitted data instead of creating a new one.
        user_form = UserForm(request.POST, instance=user)
        staff_form = StaffForm(request.POST, instance=staff)
        if user_form.save() and staff_form.save():
            user_form.save() # updates existing object
            staff_form.save()
            messages.success(request, 'Staff updated successfully.')
            return redirect('staff:list')

    else:
        # instance=staff tells Django: “This form is bound to this specific Staff object from the database.
        user_form = UserForm(instance=user) # Create a form pre-filled with the staff's current data allows the user to see existing data.
        staff_form = StaffForm(instance=staff)

    # Render the form template
    return render(request, 'staff/staff_update.html', {'user_form': user_form, 'staff_form': staff_form, 'title': 'Update Staff'})

# ----------------------------------------------------------------
# Delete a staff member
# ----------------------------------------------------------------
# @login_required
def delete_staff(request, pk):
    logged_in_user = Staff.objects.filter(user = request.user).first()
    staff_to_delete = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff_to_delete.user.delete()  # Delete the object,  Cascade deletes Staff too
        # Add a one-time success message that will be displayed to the user after deletion
        messages.success(request, 'Staff deleted successfully.')
        return redirect('staff:list') # Redirect to the list page after deletion
    # If not POST, render a confirmation template
    return render(request, 'staff/staff_delete.html', {
        'staff': logged_in_user, 
        'staff_to_delete': staff_to_delete}) 