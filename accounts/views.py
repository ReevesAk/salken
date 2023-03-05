from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from . forms import RegistrationForm
from .models import Account

# Create your views here.

# register handles the POST request to register a user.
def register(request):
    if request.method == 'POST':
        form =  form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_no = form.cleaned_data['phone_no']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            username = first_name + last_name

            user = Account.objects.create_user(
                                                first_name=first_name, 
                                                last_name=last_name, 
                                                username=username,
                                                email=email,
                                                password=password)
            user.phone_no = phone_no
            user.save(self)
            messages.success(request, 'Registration was susscessful')
            return redirect('register')
    else:
        form = RegistrationForm
        
    context = {
        'form': form
    }
    return render(request=request, template_name='accounts/register.html', context=context)


# login handles the POST request to login a user.
def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user != None:
            auth.login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials!")
            return redirect('login')
    return render(request=request, template_name='accounts/login.html')    


# logout handles the POST request to logout a user.
@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out")
    return redirect("login")
    render(request=request, template_name='accounts/logout.html')       
