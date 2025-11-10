from functools import wraps
from flask_login import current_user
from flask import abort, flash, redirect, url_for
from .models import Patient, Admin, Doctor

"""
i have used these decorator to restain other roles to access each others dashboard and routes
where, in the first rout it checks if the user is logged in or not, if not then redirect to login page
then it checks if the current_user is instance of the required role, if not then it shows forbidden error 403
if both conditions are satisfied then it allows to access the route
"""
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('admin.login')) 
        
        if not isinstance(current_user, Admin):
            flash("You do not have permission to access this page.", "danger")
            abort(403) 
            
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('admin.login')) 
        if not isinstance(current_user, Doctor):
            flash("You do not have permission to access this page.", "danger")
            abort(403) 
            
        return f(*args, **kwargs)
    return decorated_function


def patient_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", "danger")
            return redirect(url_for('admin.login')) 
        if not isinstance(current_user, Patient):
            flash("You do not have permission to access this page.", "danger")
            abort(403) # Forbidden error
            
        return f(*args, **kwargs)
    return decorated_function

