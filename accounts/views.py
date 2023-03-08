from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from . forms import RegistrationForm
from .models import Account
from django.http import HttpResponse

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


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

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = "Follow the link to activate your account"
            message = render_to_string('aaccounts/account_verification_email.html', {
                "user": user,
                "domain": current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user), 
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect('/accounts/login/?command=verification&email='+email)
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


# activate handles the GET response for account verification via email.
def activate(request, uidb64, token ):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')    

