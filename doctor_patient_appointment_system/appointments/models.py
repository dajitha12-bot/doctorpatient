
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    average_consultation_minutes = models.IntegerField(default=10)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.name} - Specialization: {self.specialization}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('BOOKED', 'Booked'),
        ('CONFIRMED', 'Confirmed'),
        ('ARRIVED', 'Arrived'),
        ('WAITING', 'Waiting'),
        ('CONSULTING', 'Consulting'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('NORMAL', 'Normal'),
        ('EMERGENCY', 'Emergency'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True, null=True)

    token_number = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NORMAL')
    consultation_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    arrived_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Appt {self.id} - {self.patient.username} with {self.doctor.name}"

class Notification(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"To {self.patient.username}: {self.message}"
