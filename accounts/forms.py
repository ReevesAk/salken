from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholders': 'Enter Password',
                'class': 'form-control',
            }
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_no', 'email', 'password']

    # overrides the registration fields and apply bootstrap form control method to
    # all the form fields.
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_no'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        # An unsaved account lets the similarity validator compare the
        # password with the name and email being registered.
        applicant = Account(
            first_name=cleaned_data.get('first_name', ''),
            last_name=cleaned_data.get('last_name', ''),
            email=cleaned_data.get('email', ''),
        )
        _clean_new_password(self, 'password', 'passwords do not match', applicant)
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=100)
    password = forms.CharField(strip=False, widget=forms.PasswordInput)


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(max_length=100)


# _clean_new_password checks that a new password matches its confirmation and
# passes AUTH_PASSWORD_VALIDATORS. user lets the similarity validator compare
# the password with the user's name and email.
def _clean_new_password(form, field, mismatch_message, user=None):
    password = form.cleaned_data.get(field)
    confirmation = form.cleaned_data.get('confirm_password')
    if password is None or confirmation is None:
        return
    if password != confirmation:
        raise forms.ValidationError(mismatch_message)
    try:
        validate_password(password, user=user)
    except forms.ValidationError as error:
        form.add_error(field, error)


class SetPasswordForm(forms.Form):
    password = forms.CharField(strip=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        _clean_new_password(self, 'password', 'Passwords do not match!', self.user)
        return cleaned_data


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(strip=False, widget=forms.PasswordInput)
    new_password = forms.CharField(strip=False, widget=forms.PasswordInput)
    confirm_password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, *args, user, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_current_password(self):
        current_password = self.cleaned_data['current_password']
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Please enter valid current password')
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        _clean_new_password(self, 'new_password', 'Password does not match!', self.user)
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_no')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(
        required=False,
        error_messages={'invalid': ("Image files only")},
        widget=forms.FileInput,
    )

    class Meta:
        model = UserProfile
        fields = (
            'address_line_1',
            'address_line_2',
            'city',
            'state',
            'country',
            'profile_picture',
        )

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
