from django import forms
from .models import Profile, Order, Sweet
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['address', 'phone']

class OrderForm(forms.ModelForm):
    sweet = forms.ModelChoiceField(queryset=Sweet.objects.all(), empty_label="Select Sweet")

    class Meta:
        model = Order
        fields = ['sweet', 'quantity']