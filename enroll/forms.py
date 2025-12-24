from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-lg glass-input"
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control form-control-lg glass-input"
            })
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'description']

from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'title', 'message']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].required = False
        self.fields['user'].empty_label = "All Users"