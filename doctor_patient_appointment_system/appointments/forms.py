from django import forms
from .models import Appointment, Doctor, UserProfile
from django.contrib.auth.models import User

class UserRegisterForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 9876543210'}),
        label="Phone Number",
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

class DoctorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Dr. {obj.name} - {obj.specialization} ({obj.available_times})"

class AppointmentForm(forms.ModelForm):
    specialization = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_specialization'}),
        required=False,
        label="Doctor Specialization"
    )
    doctor = DoctorModelChoiceField(
        queryset=Doctor.objects.filter(available=True),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_doctor'}),
        empty_label="-- Select Doctor --",
        label="Select Doctor"
    )

    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Reason for visit (e.g. Chest pain, Fever, Skin rash...)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        specs = Doctor.objects.values_list('specialization', flat=True).distinct()
        choices = [('', '-- All Specializations --')] + [(s, s) for s in specs]
        self.fields['specialization'].choices = choices

class PatientProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False)
    phone_number = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}), required=False)
