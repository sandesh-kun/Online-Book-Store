from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Address
from .models import CustomUser  # Import the CustomUser model

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
