from django import forms # Import the Django forms system
from .models import Staff # The dot (.) means from the current app, import the model named Staff.
import datetime  # Python’s standard datetime module, which lets you work with dates and times in Django models

class StaffForm(forms.ModelForm): # allows you to automatically create a form based on a database model.
    class Meta: # provide configuration 
        model = Staff # the model tied to the form
        fields = ['user', 'role', 'phone_number', 'date_hired'] # Which fields should appear
        widgets = {
            'date_hired': forms.DateInput(attrs={'type' : 'date'}),
        }
        error_messages = {
            'user': { # The field you are customizing errors for
                'required': "Please select a user for this staff member." # The type of error and the message shown to the user when the validation fails
            },
            'role': {
                'required': "Please select the role (Manager or Attendant)."  
            },
            'phone_number': {
                'invalid': "Please enter a valid phone number (9-15 digits)." # Validation fails        
            },
            'date_hired': {
                'invalid': "Please enter a valid date."
            }            
        }

        """
        custom field-level validation method
        Django calls clean_<fieldname>() automatically when you run form.is_valid().

        """
        def clean_phone_number(self): # cleaned_data is a dictionary that holds all the validated and cleaned form input values after form.is_valid() has been called
            phone = self.cleaned_data.get('phone_number') # Looks for the value under the 'phone_number' key Returns the value if it exists, Returns None if it doesn’t exist (avoids error)

            if phone and not phone.replace('+', '').isdigit():
                raise forms.ValidationError(
                "Phone number must contain only digits and optional + sign."
                )
            
            # Every clean_<field>() method must return the cleaned value or the field will be lost.
            return phone #this puts the validated phone number back into cleaned_data
        
        def clean_date_hired(self):
            date_hired = self.cleaned_data.get('date_hired')

            if date_hired and date_hired > datetime.date.today():
                raise forms.ValidationError("Date hired cannot be in the future.")
            
            return date_hired 