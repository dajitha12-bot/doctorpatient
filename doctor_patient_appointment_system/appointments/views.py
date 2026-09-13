from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Doctor, Appointment, Notification, UserProfile
from .forms import UserRegisterForm, AppointmentForm, PatientProfileForm

# Role Access Decorators
def is_receptionist_user(user):
    if not user.is_authenticated:
        return False
    if user.is_staff or user.username == 'receptionist':
        return True
    profile = getattr(user, 'profile', None)
    return profile and profile.user_type == 'RECEPTIONIST'

def receptionist_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not is_receptionist_user(request.user):
            messages.error(request, "Access denied. Receptionist portal only.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped

def patient_required(view_func):
    @login_required
    def _wrapped(request, *args, **kwargs):
        if is_receptionist_user(request.user):
            return redirect('receptionist_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped

# Common Views
def home(request):
    if request.user.is_authenticated:
        if is_receptionist_user(request.user):
            return redirect('receptionist_dashboard')
        return redirect('patient_dashboard')
    return render(request, 'home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            phone = form.cleaned_data.get('phone_number', '')
            UserProfile.objects.create(user=user, user_type='PATIENT', phone_number=phone)

            login(request, user)
            messages.success(request, "Account created successfully! Welcome to your dashboard.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Registration failed. Please fix the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

# Helper function to compute expected time
def calculate_expected_time(doctor, appt_date, appt_time, is_emergency=False):
    today_appts = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=appt_date,
        status__in=['WAITING', 'ONGOING']
    )
    if is_emergency:
        # Emergency gets immediate next slot after ongoing
        ongoing = today_appts.filter(status='ONGOING').first()
        if ongoing and ongoing.expected_time:
            dt = datetime.combine(appt_date, ongoing.expected_time) + timedelta(minutes=doctor.average_consultation_minutes)
            return dt.time()
        return appt_time

    waiting_count = today_appts.filter(status='WAITING').count()
    dt = datetime.combine(appt_date, appt_time) + timedelta(minutes=waiting_count * doctor.average_consultation_minutes)
    return dt.time()

# Patient Views
@patient_required
def patient_dashboard(request):
    today = timezone.now().date()
    active_appt = Appointment.objects.filter(
        patient=request.user,
        status__in=['WAITING', 'ONGOING']
    ).order_by('appointment_date', 'appointment_time').first()

    ongoing_appt = None
    patients_before = 0
    estimated_time = None
    is_delayed = False
    delay_amount = 0
    emergency_alert = False

    if active_appt:
        doctor_queue = list(Appointment.objects.filter(
            doctor=active_appt.doctor,
            appointment_date=active_appt.appointment_date,
            status__in=['ONGOING', 'WAITING']
        ).order_by('-priority', 'id'))

        ongoing_appt = next((a for a in doctor_queue if a.status == 'ONGOING'), None)
        
        # Calculate patients ahead
        for index, appt in enumerate(doctor_queue):
            if appt.id == active_appt.id:
                patients_before = index
                break

        estimated_time = active_appt.expected_time or active_appt.appointment_time
        if active_appt.delay_minutes > 0:
            is_delayed = True
            delay_amount = active_appt.delay_minutes

        if any(a.priority == 'EMERGENCY' for a in doctor_queue if a.id != active_appt.id):
            emergency_alert = True

    context = {
        'active_appt': active_appt,
        'ongoing_appt': ongoing_appt,
        'patients_before': patients_before,
        'queue_position': patients_before + 1 if active_appt else 0,
        'estimated_time': estimated_time,
        'is_delayed': is_delayed,
        'delay_amount': delay_amount,
        'emergency_alert': emergency_alert,
    }
    return render(request, 'patient_dashboard.html', context)

@patient_required
def patient_book(request):
    selected_doc_id = request.GET.get('doctor_id')
    initial_data = {}
    if selected_doc_id:
        try:
            doc = Doctor.objects.get(id=selected_doc_id)
            initial_data['doctor'] = doc
            initial_data['specialization'] = doc.specialization
        except Doctor.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = request.user
            appt.status = 'WAITING'
            appt.priority = 'NORMAL'
            
            # Calculate expected time
            appt.expected_time = calculate_expected_time(
                appt.doctor, appt.appointment_date, appt.appointment_time
            )
            appt.token_number = f"T-{100 + appt.id if appt.id else Appointment.objects.count() + 101}"
            appt.save()
            
            # Auto-generate notification
            Notification.objects.create(
                patient=request.user,
                notification_type='BOOKED',
                message=f"Appointment #{appt.id} booked with Dr. {appt.doctor.name} ({appt.doctor.specialization}) for {appt.appointment_date} at {appt.appointment_time.strftime('%I:%M %p')}."
            )

            messages.success(request, f"Appointment #{appt.id} booked successfully!")
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm(initial=initial_data)

    doctors = Doctor.objects.filter(available=True)
    return render(request, 'patient_book.html', {'form': form, 'doctors': doctors})

@patient_required
def patient_appointments(request):
    all_appts = Appointment.objects.filter(patient=request.user).order_by('-appointment_date', '-appointment_time')
    context = {
        'upcoming_appts': all_appts.filter(status='WAITING'),
        'ongoing_appts': all_appts.filter(status='ONGOING'),
        'completed_appts': all_appts.filter(status='COMPLETED'),
        'cancelled_appts': all_appts.filter(status='CANCELLED'),
        'all_appts': all_appts,
    }
    return render(request, 'patient_appointments.html', context)

@patient_required
def patient_tracking(request):
    active_appt = Appointment.objects.filter(
        patient=request.user,
        status__in=['WAITING', 'ONGOING']
    ).order_by('appointment_date', 'appointment_time').first()

    queue_list = []
    ongoing_appt = None
    patients_ahead = 0
    user_position = 0

    if active_appt:
        queue_list = Appointment.objects.filter(
            doctor=active_appt.doctor,
            appointment_date=active_appt.appointment_date
        ).order_by('id')

        ongoing_appt = queue_list.filter(status='ONGOING').first()

        waiting_queue = list(queue_list.filter(status__in=['ONGOING', 'WAITING']).order_by('-priority', 'id'))
        for idx, item in enumerate(waiting_queue):
            if item.id == active_appt.id:
                user_position = idx + 1
                patients_ahead = idx
                break

    context = {
        'active_appt': active_appt,
        'queue_list': queue_list,
        'ongoing_appt': ongoing_appt,
        'patients_ahead': patients_ahead,
        'user_position': user_position,
    }
    return render(request, 'patient_tracking.html', context)

@patient_required
def patient_notifications(request):
    notifications = Notification.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'patient_notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, patient=request.user)
    notif.is_read = True
    notif.save()
    return redirect('patient_notifications')

@patient_required
def patient_profile(request):
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST)
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            profile.phone_number = form.cleaned_data['phone_number']
            profile.save()

            messages.success(request, "Profile details updated successfully.")
            return redirect('patient_profile')
    else:
        form = PatientProfileForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': profile.phone_number,
        })

    return render(request, 'patient_profile.html', {'form': form, 'profile': profile})

# Receptionist Views (5 Pages Only)

@receptionist_required
def receptionist_dashboard(request):
    today = timezone.now().date()
    today_appts = Appointment.objects.filter(appointment_date=today)

    total_count = today_appts.count()
    waiting_count = today_appts.filter(status='WAITING').count()
    ongoing_count = today_appts.filter(status='ONGOING').count()
    completed_count = today_appts.filter(status='COMPLETED').count()
    emergency_count = today_appts.filter(priority='EMERGENCY').count()
    delayed_count = today_appts.filter(delay_minutes__gt=0).count()

    live_queue = today_appts.filter(status__in=['ONGOING', 'WAITING']).order_by('-priority', 'id')
    ongoing = live_queue.filter(status='ONGOING').first()
    next_patients = live_queue.filter(status='WAITING')[:3]

    context = {
        'total_count': total_count,
        'waiting_count': waiting_count,
        'ongoing_count': ongoing_count,
        'completed_count': completed_count,
        'emergency_count': emergency_count,
        'delayed_count': delayed_count,
        'ongoing': ongoing,
        'next_patients': next_patients,
        'live_queue': live_queue,
    }
    return render(request, 'receptionist_dashboard.html', context)

@receptionist_required
def receptionist_appointments(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'ALL')

    appts = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')

    if query:
        if query.startswith('#') and query[1:].isdigit():
            appts = appts.filter(id=int(query[1:]))
        elif query.isdigit():
            appts = appts.filter(id=int(query))
        else:
            appts = appts.filter(patient__username__icontains=query) | appts.filter(patient__first_name__icontains=query)

    if status_filter != 'ALL':
        appts = appts.filter(status=status_filter)

    context = {
        'appts': appts,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'receptionist_appointments.html', context)

@receptionist_required
def complete_appointment_action(request, appt_id):
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appt_id)
        appt.status = 'COMPLETED'
        appt.completed_at = timezone.now()
        appt.save()

        # Auto Notification for completed patient
        Notification.objects.create(
            patient=appt.patient,
            notification_type='COMPLETED',
            message=f"Your appointment #{appt.id} with Dr. {appt.doctor.name} has been COMPLETED. Thank you!"
        )

        # Select next eligible waiting appointment for doctor
        next_appt = Appointment.objects.filter(
            doctor=appt.doctor,
            appointment_date=appt.appointment_date,
            status='WAITING'
        ).order_by('-priority', 'id').first()

        if next_appt:
            next_appt.status = 'ONGOING'
            next_appt.save()

            # Auto Notification for next patient
            Notification.objects.create(
                patient=next_appt.patient,
                notification_type='GENERAL',
                message=f"🎫 IT'S YOUR TURN! Appointment #{next_appt.id} is now ONGOING. Please proceed to Dr. {next_appt.doctor.name}'s room."
            )
            messages.success(request, f"Appointment #{appt.id} marked COMPLETED. Appointment #{next_appt.id} is now ONGOING.")
        else:
            messages.success(request, f"Appointment #{appt.id} marked COMPLETED.")

    return redirect('receptionist_appointments')

@receptionist_required
def receptionist_queue(request):
    today = timezone.now().date()
    queue = Appointment.objects.filter(
        appointment_date=today,
        status__in=['ONGOING', 'WAITING']
    ).order_by('-priority', 'id')

    return render(request, 'receptionist_queue.html', {'queue': queue})

@receptionist_required
def mark_emergency_action(request, appt_id):
    if request.method == 'POST':
        appt = get_object_or_404(Appointment, id=appt_id)
        appt.priority = 'EMERGENCY'
        appt.save()

        # Auto Notification to emergency patient
        Notification.objects.create(
            patient=appt.patient,
            notification_type='EMERGENCY',
            message=f"🚨 EMERGENCY PRIORITY: Your appointment #{appt.id} has been marked as Emergency Priority."
        )

        # Auto Notification to other waiting patients of same doctor
        other_waiting = Appointment.objects.filter(
            doctor=appt.doctor,
            appointment_date=appt.appointment_date,
            status='WAITING'
        ).exclude(id=appt.id)

        for other in other_waiting:
            Notification.objects.create(
                patient=other.patient,
                notification_type='DELAY',
                message=f"🚨 EMERGENCY ALERT: An emergency patient was prioritized for Dr. {appt.doctor.name}. Your estimated waiting time may be adjusted."
            )

        messages.success(request, f"Appointment #{appt.id} marked as EMERGENCY priority!")
    return redirect('receptionist_queue')

@receptionist_required
def receptionist_delay(request):
    today = timezone.now().date()
    waiting_appts = Appointment.objects.filter(
        appointment_date=today,
        status__in=['ONGOING', 'WAITING']
    ).order_by('-priority', 'id')

    return render(request, 'receptionist_delay.html', {'waiting_appts': waiting_appts})

@receptionist_required
def apply_delay_action(request):
    if request.method == 'POST':
        minutes = int(request.POST.get('minutes', 10))
        today = timezone.now().date()

        waiting_appts = Appointment.objects.filter(
            appointment_date=today,
            status='WAITING'
        )

        for appt in waiting_appts:
            appt.delay_minutes += minutes
            if appt.expected_time:
                dt = datetime.combine(today, appt.expected_time) + timedelta(minutes=minutes)
                appt.expected_time = dt.time()
            appt.save()

            # Auto delay notification to affected patient
            new_time_str = appt.expected_time.strftime('%I:%M %p') if appt.expected_time else 'updated time'
            Notification.objects.create(
                patient=appt.patient,
                notification_type='DELAY',
                message=f"⚠️ APPOINTMENT DELAY: Your appointment #{appt.id} is delayed by approximately {minutes} minutes. Updated expected time: {new_time_str}."
            )

        messages.success(request, f"Applied +{minutes} MIN delay to {waiting_appts.count()} waiting appointments.")
    return redirect('receptionist_delay')

@receptionist_required
def receptionist_management(request):
    doctors = Doctor.objects.all()
    patients = User.objects.filter(is_staff=False, is_superuser=False).exclude(username='receptionist')
    
    # Calculate appointment count per patient
    patient_list = []
    for p in patients:
        count = Appointment.objects.filter(patient=p).count()
        profile, _ = UserProfile.objects.get_or_create(user=p)
        patient_list.append({
            'user': p,
            'phone': profile.phone_number or 'N/A',
            'count': count
        })

    context = {
        'doctors': doctors,
        'patient_list': patient_list,
        'receptionist_user': request.user,
    }
    return render(request, 'receptionist_management.html', context)
