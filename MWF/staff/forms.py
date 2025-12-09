from django import forms # Import the Django forms system
from django.contrib.auth.models import User
from .models import Staff # The dot (.) means from the current app, import the model named Staff.
import datetime  # Python’s standard datetime module, which lets you work with dates and times in Django models

class StaffUserForm(forms.ModelForm): # allows you to automatically create a form based on a database model.
    # form that handles both the Django User model and custom Staff model

    # User fields
    first_name = forms.CharField(max_length=30, required=True, error_messages={
        'required': "Please enter your first name.",
        'max_length': "Username cannot be longer than 30 characters." })
    last_name = forms.CharField(max_length=30, required=True, error_messages={
        'required': "Please enter your last name.",
        'max_length': "Username cannot be longer than 30 characters." })
    username = forms.CharField(max_length=100, required=True, error_messages={
        'required': "Please enter a username.",
        'max_length': "Username cannot be longer than 100 characters." }) # User's email address; required, uniqueness validation added below
    email = forms.EmailField(required=True,  error_messages={
        'required': "Please enter an email address.",
        'invalid': "Please enter a valid email address."
    })
    password = forms.CharField(widget=forms.PasswordInput, required=True,  error_messages={
        'required': "Please enter a password."
    })  # Password field; required; input is masked
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password', required=True, error_messages={
        'required': "Please confirm your password."
    }
)

    # Staff fields
    class Meta: # provide configuration 
        model = Staff # the model tied to the form
        fields = ['role', 'phone_number', 'date_hired'] # Which fields should appear
        widgets = {
            'date_hired': forms.DateInput(attrs={'type' : 'date'}),
        }
        error_messages = {
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
    def clean_username(self): # cleaned_data is a dictionary that holds all the validated and cleaned form input values after form.is_valid() has been called
        """
        Ensure the username is unique in the database.
        Raises ValidationError if the username already exists.
        """
        username = self.cleaned_data.get('username') # Looks for the value under the 'username' key Returns the value if it exists, Returns None if it doesn’t exist (avoids error)
        if User.objects.filter(username = username).exists():
            raise forms.ValidationError("Username already exists.")
        
        # Every clean_<field>() method must return the cleaned value or the field will be lost.
        return username #this puts the validated username back into cleaned_data
    
    def clean_password2(self):
        """
        Check that password and password2 fields match.
        Raises ValidationError if they do not match.
        """
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError("Passwords do not match.") 
        return password2
        
    def clean_email(self):   
        """
        Ensure the username is unique in the database.
        Raises ValidationError if the username already exists.
        """

        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email
        
    def clean_phone_number(self): 
        phone = self.cleaned_data.get('phone_number') 

        if phone and not phone.replace('+', '').isdigit():
            raise forms.ValidationError(
            "Phone number must contain only digits and optional + sign."
            )
        
        return phone 
    
    def clean_date_hired(self):
        date_hired = self.cleaned_data.get('date_hired')

        if date_hired and date_hired > datetime.date.today():
            raise forms.ValidationError("Date hired cannot be in the future.")
        
        return date_hired 
    
    def save(self, commit = True):
        # Create the user first
        user = User.objects.create_user(
            username = self.cleaned_data['username'],
            email = self.cleaned_data['email'],
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            password = self.cleaned_data['password']
        )

        # Create Staff linked to the user
        # calls the original ModelForm.save() method — it builds a Staff object from the form fields.
        # commit=False - don’t save it to the database yet, since: we haven't created and attach the User yet
        staff = super().save(commit = False)
        staff.user = user # attach the newly created User to the Staff object

        if commit:
            staff.save() # writes the Staff record into the database

        return staff # makes the saved staff object available to whatever code called the form
        

    # ----------------------------
# Separate forms for updating Staff and User
# ----------------------------
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['role', 'phone_number', 'date_hired']
        widgets = {
            'date_hired': forms.DateInput(attrs={'type':'date'})
        }
