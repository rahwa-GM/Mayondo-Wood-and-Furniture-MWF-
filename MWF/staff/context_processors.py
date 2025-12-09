from .models import Staff

def staff_role(request):
    staff = None # default in case the user is not logged in.

    if request.user.is_authenticated: # only look for staff if the user is logged in.
        # Staff.objects.filter(user=request.user) fetches the Staff object for the currently logged-in user.
        # .first() ensures it returns either one Staff object or None (if not found).
        staff = Staff.objects.filter(user = request.user).first()
    return({'staff': staff}) # makes the variable staff available in all templates.
    



    