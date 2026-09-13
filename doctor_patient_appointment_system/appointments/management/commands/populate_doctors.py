
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from appointments.models import Doctor

class Command(BaseCommand):
    help = 'Populates database with initial Receptionist, Doctors, and Patients'

    def handle(self, *args, **kwargs):
        # 1. Receptionist / Admin User
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

        # 2. Doctors
        doctors_data = [
            {'username': 'dr_arun', 'name': 'Arun Kumar', 'specialization': 'Cardiology', 'avg_time': 10},
            {'username': 'dr_priya', 'name': 'Priya Sharma', 'specialization': 'Neurology', 'avg_time': 15},
            {'username': 'dr_rajesh', 'name': 'Rajesh Patel', 'specialization': 'Orthopedics', 'avg_time': 12},
            {'username': 'dr_sunita', 'name': 'Sunita Verma', 'specialization': 'Pediatrics', 'avg_time': 8},
            {'username': 'dr_vikram', 'name': 'Vikram Singh', 'specialization': 'General Medicine', 'avg_time': 10},
            {'username': 'dr_ananya', 'name': 'Ananya Roy', 'specialization': 'Dermatology', 'avg_time': 10},
        ]

        for d in doctors_data:
            first = d['name'].split()[0]
            last = d['name'].split()[-1]
            user, created = User.objects.get_or_create(
                username=d['username'],
                defaults={'first_name': first, 'last_name': last, 'email': f"{d['username']}@hospital.com"}
            )
            if created:
                user.set_password('doctor123')
                user.save()

            doctor, doc_created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'name': d['name'],
                    'specialization': d['specialization'],
                    'average_consultation_minutes': d['avg_time'],
                    'available': True
                }
            )
            if doc_created:
                self.stdout.write(self.style.SUCCESS(f"Created Doctor: Dr. {d['name']} ({d['specialization']})"))

        # 3. Patients
        patients_data = [
            {'username': 'patient1', 'first_name': 'Rahul', 'last_name': 'Sharma', 'email': 'patient1@gmail.com'},
            {'username': 'patient2', 'first_name': 'Sneha', 'last_name': 'Gupta', 'email': 'patient2@gmail.com'},
            {'username': 'patient3', 'first_name': 'Amit', 'last_name': 'Verma', 'email': 'patient3@gmail.com'},
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
