from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.core.exceptions import PermissionDenied

# User Registration
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'booking/register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'booking/login.html')

# User Logout
def user_logout(request):
    logout(request)
    return redirect('login')

# Dashboard (Redirect based on user type)
@login_required
def dashboard(request):
    if request.user.is_admin():
        return redirect('admin_dashboard')
    return redirect('passenger_dashboard')

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_admin():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    return wrap

@login_required
@admin_required
def manage_buses(request):
    return render(request, 'booking/admin_dashboard.html')



