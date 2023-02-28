from django.shortcuts import render
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
    else:
        form = RegistrationForm
        
    context = {
        'form': form
    }
    return render(request=request, template_name='accounts/register.html', context=context)


# login handles the POST request to login a user.
def login(request):
    return render(request=request, template_name='accounts/login.html')    


# logout handles the POST request to logout a user.
def logout(request):
    render(request=request, template_name='accounts/logout.html')       
