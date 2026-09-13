
from django import forms
from .models import Appointment, Doctor
from django.contrib.auth.models import User

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class DoctorModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Dr. {obj.name} ({obj.specialization})"

class AppointmentForm(forms.ModelForm):
    doctor = DoctorModelChoiceField(
        queryset=Doctor.objects.filter(available=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select Doctor & Specialization --"
    )
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Reason for visit (optional)'}),
        }
