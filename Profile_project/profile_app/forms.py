from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Address, Review, CustomUser


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser  # Use CustomUser instead of User
        fields = ['username', 'email', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser  # Use CustomUser instead of User
        fields = ['username', 'password']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address', 'city', 'state', 'pincode']
        labels = {
            'address': 'Address',
            'city': 'City',
            'state': 'State',
            'pincode': 'Pincode'
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6)
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Rating (1-5)',
            'comment': 'Comment'
        }