# people/decorators.py - Create permission decorators

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def startup_required(view_func):
    """Decorator to check if user has a startup"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.startup:
            messages.error(request, 'You need to have a startup to access this page.')
            return redirect('startup_profile_setup')
        return view_func(request, *args, **kwargs)
    return wrapper


def startup_admin_required(view_func):
    """Decorator to check if user is a startup admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_startup_admin() and not request.user.is_super_admin():
            messages.error(request, 'You need admin privileges to access this page.')
            return redirect('people_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def startup_hr_required(view_func):
    """Decorator to check if user is a startup HR"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_startup_hr() or request.user.is_startup_admin() or request.user.is_super_admin()):
            messages.error(request, 'You need HR privileges to access this page.')
            return redirect('people_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper