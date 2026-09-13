from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time, timedelta
from appointments.models import Doctor, UserProfile, Appointment, Notification

class Command(BaseCommand):
    help = 'Populates database with initial Receptionist user, default Doctors, demo Patients, and sample Appointments for all doctors'

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

        # 2. Default Doctors (Including Rajesh Patel & Sunita Verma)
        default_doctors = [
            {'name': 'Arun Kumar', 'specialization': 'Cardiology', 'avg_time': 15, 'days': 'Mon - Sat', 'times': '09:00 AM - 04:00 PM'},
            {'name': 'Priya', 'specialization': 'Dermatology', 'avg_time': 10, 'days': 'Mon - Fri', 'times': '10:00 AM - 05:00 PM'},
            {'name': 'Ravi', 'specialization': 'Orthopedics', 'avg_time': 15, 'days': 'Mon - Sat', 'times': '09:30 AM - 03:30 PM'},
            {'name': 'Meena', 'specialization': 'General Medicine', 'avg_time': 10, 'days': 'Mon - Sun', 'times': '08:00 AM - 06:00 PM'},
            {'name': 'Karthik', 'specialization': 'Neurology', 'avg_time': 20, 'days': 'Tue - Sat', 'times': '10:00 AM - 04:00 PM'},
            {'name': 'Sunita Verma', 'specialization': 'Pediatrics', 'avg_time': 10, 'days': 'Mon - Sat', 'times': '09:00 AM - 05:00 PM'},
            {'name': 'Rajesh Patel', 'specialization': 'Orthopedics', 'avg_time': 15, 'days': 'Mon - Sat', 'times': '09:00 AM - 04:00 PM'},
        ]

        doctors_dict = {}
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
            doctors_dict[d['name']] = doc
            if doc_created:
                self.stdout.write(self.style.SUCCESS(f"Created Default Doctor: Dr. {d['name']} ({d['specialization']})"))

        # 3. Patient Demo Users
        patients_data = [
            {'username': 'patient1', 'first_name': 'Rahul', 'last_name': 'Sharma', 'email': 'patient1@gmail.com', 'phone': '9876543210'},
            {'username': 'patient2', 'first_name': 'Sneha', 'last_name': 'Gupta', 'email': 'patient2@gmail.com', 'phone': '9876543211'},
            {'username': 'patient3', 'first_name': 'Amit', 'last_name': 'Verma', 'email': 'patient3@gmail.com', 'phone': '9876543212'},
            {'username': 'patient4', 'first_name': 'Anika', 'last_name': 'Patel', 'email': 'patient4@gmail.com', 'phone': '9876543213'},
            {'username': 'patient5', 'first_name': 'Kiran', 'last_name': 'Kumar', 'email': 'patient5@gmail.com', 'phone': '9876543214'},
        ]

        users_dict = {}
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
            users_dict[p['username']] = user

        # Clear existing appointments & notifications
        Appointment.objects.all().delete()
        Notification.objects.all().delete()

        # 4. Sample Demo Appointments across ALL doctors for today (Completed, Ongoing, Waiting)
        today = timezone.now().date()

        sample_appts = [
            # Dr. Arun Kumar
            {'patient': users_dict['patient1'], 'doctor': doctors_dict['Arun Kumar'], 'date': today, 'time': time(9, 0), 'expected_time': time(9, 0), 'reason': 'Routine Checkup', 'status': 'COMPLETED', 'priority': 'NORMAL', 'token': 'T-101'},
            {'patient': users_dict['patient2'], 'doctor': doctors_dict['Arun Kumar'], 'date': today, 'time': time(9, 15), 'expected_time': time(9, 15), 'reason': 'Cardiac Consultation', 'status': 'ONGOING', 'priority': 'NORMAL', 'token': 'T-102'},
            {'patient': users_dict['patient3'], 'doctor': doctors_dict['Arun Kumar'], 'date': today, 'time': time(9, 30), 'expected_time': time(9, 30), 'reason': 'Chest Pain Evaluation', 'status': 'WAITING', 'priority': 'NORMAL', 'token': 'T-103'},

            # Dr. Rajesh Patel
            {'patient': users_dict['patient4'], 'doctor': doctors_dict['Rajesh Patel'], 'date': today, 'time': time(8, 30), 'expected_time': time(8, 30), 'reason': 'Fracture Checkup', 'status': 'COMPLETED', 'priority': 'NORMAL', 'token': 'T-201'},
            {'patient': users_dict['patient5'], 'doctor': doctors_dict['Rajesh Patel'], 'date': today, 'time': time(8, 45), 'expected_time': time(8, 45), 'reason': 'Joint Stiffness', 'status': 'ONGOING', 'priority': 'NORMAL', 'token': 'T-202'},

            # Dr. Sunita Verma
            {'patient': users_dict['patient1'], 'doctor': doctors_dict['Sunita Verma'], 'date': today, 'time': time(8, 30), 'expected_time': time(8, 30), 'reason': 'Pediatric Allergy Check', 'status': 'COMPLETED', 'priority': 'NORMAL', 'token': 'T-301'},
            {'patient': users_dict['patient2'], 'doctor': doctors_dict['Sunita Verma'], 'date': today, 'time': time(8, 45), 'expected_time': time(8, 45), 'reason': 'Child Vaccination', 'status': 'ONGOING', 'priority': 'NORMAL', 'token': 'T-302'},

            # Dr. Priya
            {'patient': users_dict['patient3'], 'doctor': doctors_dict['Priya'], 'date': today, 'time': time(9, 0), 'expected_time': time(9, 0), 'reason': 'Skin Rash Consultation', 'status': 'COMPLETED', 'priority': 'NORMAL', 'token': 'T-401'},
            {'patient': users_dict['patient4'], 'doctor': doctors_dict['Priya'], 'date': today, 'time': time(9, 10), 'expected_time': time(9, 10), 'reason': 'Acne Consultation', 'status': 'WAITING', 'priority': 'NORMAL', 'token': 'T-402'},

            # Dr. Meena
            {'patient': users_dict['patient4'], 'doctor': doctors_dict['Meena'], 'date': today, 'time': time(8, 0), 'expected_time': time(8, 0), 'reason': 'Flu & Fever Treatment', 'status': 'COMPLETED', 'priority': 'NORMAL', 'token': 'T-501'},
            {'patient': users_dict['patient1'], 'doctor': doctors_dict['Meena'], 'date': today, 'time': time(8, 10), 'expected_time': time(8, 10), 'reason': 'General Fatigue', 'status': 'WAITING', 'priority': 'NORMAL', 'token': 'T-502'},

            # Dr. Karthik
            {'patient': users_dict['patient5'], 'doctor': doctors_dict['Karthik'], 'date': today, 'time': time(9, 30), 'expected_time': time(9, 30), 'reason': 'Migraine Evaluation', 'status': 'ONGOING', 'priority': 'NORMAL', 'token': 'T-601'},
        ]

        for sa in sample_appts:
            appt = Appointment.objects.create(
                patient=sa['patient'],
                doctor=sa['doctor'],
                appointment_date=sa['date'],
                appointment_time=sa['time'],
                expected_time=sa['expected_time'],
                reason=sa['reason'],
                status=sa['status'],
                priority=sa['priority'],
                token_number=sa['token'],
            )
            self.stdout.write(self.style.SUCCESS(f"Created Sample Appt #{appt.id} ({sa['status']}) for {sa['patient'].username} with Dr. {sa['doctor'].name}"))

        self.stdout.write(self.style.SUCCESS("Database successfully populated with sample appointments across all doctors!"))
