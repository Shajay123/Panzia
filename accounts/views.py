from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import RegisterForm



def register_view(request):

    form = RegisterForm()

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            if user.is_superuser:

                return redirect(
                    "admin_dashboard"
                )

            return redirect(
                "home"
            )

    return render(
        request,
        "accounts/register.html",
        {"form": form}
    )


from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin
            if user.is_superuser:

                return redirect(
                    "admin_dashboard"
                )

            # Normal users
            return redirect(
                "home"
            )

        else:

            messages.error(
                request,
                "Invalid username or password"
            )

    return render(
        request,
        "accounts/login.html"
    )



def logout_view(request):
    logout(request)
    return redirect('home')