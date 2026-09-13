from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Doctor, UserProfile

class Command(BaseCommand):
    help = 'Populates database with initial Receptionist user, default Doctors, and demo Patients'

    def handle(self, *args, **kwargs):
        # 1. Receptionist User
        rec_user, created = User.objects.get_or_create(
            username='receptionist',
            defaults={
                'first_name': 'Hospital',
                'last_name': 'Receptionist',
                'email': 'receptionist@hospital.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            rec_user.set_password('receptionist123')
            rec_user.save()
            self.stdout.write(self.style.SUCCESS("Created Receptionist user: receptionist / receptionist123"))

        UserProfile.objects.get_or_create(
            user=rec_user,
            defaults={'user_type': 'RECEPTIONIST', 'phone_number': '+1-555-0199'}
        )

        # 2. Default Doctors as required
        default_doctors = [
            {'name': 'Arun Kumar', 'specialization': 'Cardiology', 'avg_time': 15, 'days': 'Mon - Sat', 'times': '09:00 AM - 04:00 PM'},
            {'name': 'Priya', 'specialization': 'Dermatology', 'avg_time': 10, 'days': 'Mon - Fri', 'times': '10:00 AM - 05:00 PM'},
            {'name': 'Ravi', 'specialization': 'Orthopedics', 'avg_time': 15, 'days': 'Mon - Sat', 'times': '09:30 AM - 03:30 PM'},
            {'name': 'Meena', 'specialization': 'General Medicine', 'avg_time': 10, 'days': 'Mon - Sun', 'times': '08:00 AM - 06:00 PM'},
            {'name': 'Karthik', 'specialization': 'Neurology', 'avg_time': 20, 'days': 'Tue - Sat', 'times': '10:00 AM - 04:00 PM'},
        ]

        for d in default_doctors:
            doc, doc_created = Doctor.objects.get_or_create(
                name=d['name'],
                specialization=d['specialization'],
                defaults={
                    'average_consultation_minutes': d['avg_time'],
                    'available': True,
                    'available_days': d['days'],
                    'available_times': d['times'],
                }
            )
            if doc_created:
                self.stdout.write(self.style.SUCCESS(f"Created Default Doctor: Dr. {d['name']} ({d['specialization']})"))

        # 3. Patient Demo Users
        patients_data = [
            {'username': 'patient1', 'first_name': 'Rahul', 'last_name': 'Sharma', 'email': 'patient1@gmail.com', 'phone': '9876543210'},
            {'username': 'patient2', 'first_name': 'Sneha', 'last_name': 'Gupta', 'email': 'patient2@gmail.com', 'phone': '9876543211'},
            {'username': 'patient3', 'first_name': 'Amit', 'last_name': 'Verma', 'email': 'patient3@gmail.com', 'phone': '9876543212'},
        ]

        for p in patients_data:
            user, created = User.objects.get_or_create(
                username=p['username'],
                defaults={'first_name': p['first_name'], 'last_name': p['last_name'], 'email': p['email']}
            )
            if created:
                user.set_password('patient123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created Patient: {p['username']} / patient123"))

            UserProfile.objects.get_or_create(
                user=user,
                defaults={'user_type': 'PATIENT', 'phone_number': p['phone']}
            )
