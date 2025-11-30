"""
-----------------------------------------------------------------
Staff App Models
-----------------------------------------------------------------
This app handles all staff information.

- Staff depends on Django's built-in User model, User must exist before Staff.

- Validation is added via field validators.

"""

from django.db import models
from django.contrib.auth.models import User  # imports Django’s built-in User model.
from django.core.validators import RegexValidator  # imports Django’s RegexValidator
from django.core.exceptions import ValidationError # imports Django’s ValidationError, which is used to raise errors when data fails validation
import datetime  # Python’s standard datetime module, which lets you work with dates and times in Django models


# Create your models here.
class Staff(models.Model):  # so Django knows this class represents a database table
    """
    Model representing a staff member.
    Fields:
    - user: link to built-in User
    - role: Manager or Attendant
    - phone_number: optional, validated for correct format
    - date_hired: optional, cannot be in the future
    """

    Role_CHOICES = (("Manager", "Manager"), ("Attendant", "Attendant")) # to limit the possible values of a field

    # User: Django’s built-in authentication user model
    # OneToOneField: Each User can have only one Profile, To extend user data with custom fields
    # on_delete=models.CASCADE : If the User is deleted → profile is deleted too

    user = models.OneToOneField(User, on_delete=models.CASCADE) 
    # max_length=10 Tells the database how much space to reserve (column size)
    role = models.CharField(choices=Role_CHOICES)
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
    date_hired = models.DateField(blank=True, null=True)

    def clean(self):
        """
        Custom validation for Staff.
        - Role must be selected
        - Date hired cannot be in the future
        """

        if not self.role:
            raise ValidationError({'role': "Please select a role for the staff member."})
        if self.date_hired and self.date_hired > datetime.date.today():
            raise ValidationError({'date_hired': "Date hired cannot be in the future."})
        

    def __str__(self):
        """
        __str__ is a built-in dunder method in Python that defines the string representation of an object.        
        self.user.get_full_name() → gets the user’s first + last name
        ({self.role}) → shows the role in parentheses
        """
        return f'{self.user.get_full_name()} ({self.role})' # eg. John Doe (Manager)
    