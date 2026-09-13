
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Doctor, Appointment, Notification
from .forms import UserRegisterForm, AppointmentForm

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.username == 'receptionist':
            return redirect('receptionist_dashboard')
        elif hasattr(request.user, 'doctor'):
            return redirect('doctor_dashboard')
        return redirect('patient_dashboard')
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def doctors_list(request):
    query = request.GET.get('q', '')
    if query:
        doctors = Doctor.objects.filter(available=True).filter(
            name__icontains=query
        ) | Doctor.objects.filter(available=True).filter(
            specialization__icontains=query
        )
    else:
        doctors = Doctor.objects.filter(available=True)
    return render(request, 'doctors.html', {'doctors': doctors, 'query': query})

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-appointment_date', '-appointment_time')
    notifications = Notification.objects.filter(patient=request.user, is_read=False).order_by('-created_at')
    
    active_appt = appointments.filter(status__in=['ARRIVED', 'WAITING', 'CONSULTING']).first()
    
    context = {
        'appointments': appointments,
        'notifications': notifications,
        'active_appt': active_appt,
    }
    return render(request, 'patient_dashboard.html', context)

@login_required
def book_appointment(request):
    doctor_id = request.GET.get('doctor_id')
    initial_data = {}
    if doctor_id:
        try:
            doc = Doctor.objects.get(id=doctor_id)
            initial_data['doctor'] = doc
        except Doctor.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = request.user
            appt.status = 'CONFIRMED'
            appt.save()
            messages.success(request, "Appointment booked successfully.")
            return redirect('patient_dashboard')
    else:
        form = AppointmentForm(initial=initial_data)
    return render(request, 'book_appointment.html', {'form': form})

def generate_token(doctor, date):
    count = Appointment.objects.filter(doctor=doctor, appointment_date=date, token_number__isnull=False).count()
    return f"T-{101 + count}"

@login_required
def check_in(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, patient=request.user)
    if appt.status in ['CONFIRMED', 'BOOKED']:
        appt.status = 'WAITING'
        appt.arrived_at = timezone.now()
        appt.token_number = generate_token(appt.doctor, appt.appointment_date)
        appt.save()
        messages.success(request, f"Checked in successfully. Your token is {appt.token_number}")
    return redirect('patient_dashboard')

def get_queue(doctor, date):
    return list(Appointment.objects.filter(
        doctor=doctor, 
        appointment_date=date,
        status__in=['WAITING', 'CONSULTING']
    ).order_by('status', 'priority', 'arrived_at'))

@login_required
def patient_queue_status(request):
    active_appt = Appointment.objects.filter(patient=request.user, status__in=['WAITING', 'CONSULTING']).first()
    if not active_appt:
        return JsonResponse({'active': False})
        
    doctor = active_appt.doctor
    queue = get_queue(doctor, active_appt.appointment_date)
    
    current_serving = None
    patients_ahead = 0
    found_self = False
    
    for appt in queue:
        if appt.status == 'CONSULTING':
            current_serving = appt.token_number
            if appt == active_appt:
                found_self = True
                break
        elif appt == active_appt:
            found_self = True
            break
        else:
            patients_ahead += 1
            
    if active_appt.status == 'CONSULTING':
        patients_ahead = 0
        
    wait_time = patients_ahead * doctor.average_consultation_minutes
    
    return JsonResponse({
        'active': True,
        'status': active_appt.status,
        'own_token': active_appt.token_number,
        'current_serving': current_serving or 'None',
        'patients_ahead': patients_ahead,
        'estimated_wait': wait_time,
        'is_consulting': active_appt.status == 'CONSULTING'
    })

@login_required
def doctor_dashboard(request):
    if not hasattr(request.user, 'doctor'):
        return redirect('home')
        
    doctor = request.user.doctor
    today = timezone.now().date()
    queue = get_queue(doctor, today)
    
    current_consulting = next((a for a in queue if a.status == 'CONSULTING'), None)
    waiting_patients = [a for a in queue if a.status == 'WAITING']
    
    context = {
        'doctor': doctor,
        'current_consulting': current_consulting,
        'waiting_patients': waiting_patients,
        'today_total': Appointment.objects.filter(doctor=doctor, appointment_date=today).count(),
        'waiting_count': len(waiting_patients)
    }
    return render(request, 'doctor_dashboard.html', context)

@login_required
def receptionist_dashboard(request):
    if not (request.user.is_staff or request.user.username == 'receptionist'):
        messages.error(request, "Access denied. Receptionist/Admin only.")
        return redirect('home')

    today = timezone.now().date()
    doctors = Doctor.objects.filter(available=True)
    selected_doc_id = request.GET.get('doctor_id')
    selected_doctor = Doctor.objects.filter(id=selected_doc_id).first() if selected_doc_id else doctors.first()

    today_appts = Appointment.objects.filter(appointment_date=today).order_by('appointment_time')
    confirmed_appts = today_appts.filter(status__in=['BOOKED', 'CONFIRMED'])
    waiting_appts = today_appts.filter(status='WAITING')
    emergency_appts = today_appts.filter(priority='EMERGENCY')

    doctor_queue = []
    if selected_doctor:
        doctor_queue = get_queue(selected_doctor, today)

    context = {
        'total_doctors': Doctor.objects.count(),
        'total_patients': User.objects.filter(doctor__isnull=True, is_staff=False).count(),
        'today_total': today_appts.count(),
        'waiting_count': waiting_appts.count(),
        'emergency_count': emergency_appts.count(),
        'doctors': doctors,
        'selected_doctor': selected_doctor,
        'doctor_queue': doctor_queue,
        'confirmed_appts': confirmed_appts,
        'today_appts': today_appts,
    }
    return render(request, 'receptionist_dashboard.html', context)

@login_required
def receptionist_check_in(request, appt_id):
    if not (request.user.is_staff or request.user.username == 'receptionist'):
        return redirect('home')
    appt = get_object_or_404(Appointment, id=appt_id)
    if appt.status in ['CONFIRMED', 'BOOKED']:
        appt.status = 'WAITING'
        appt.arrived_at = timezone.now()
        appt.token_number = generate_token(appt.doctor, appt.appointment_date)
        appt.save()
        messages.success(request, f"Checked in {appt.patient.username}. Token: {appt.token_number}")
    return redirect('receptionist_dashboard')

@login_required
def call_next_patient(request):
    if not hasattr(request.user, 'doctor'):
        return redirect('home')
    doctor = request.user.doctor
    today = timezone.now().date()
    
    current = Appointment.objects.filter(doctor=doctor, appointment_date=today, status='CONSULTING').first()
    if current:
        current.status = 'COMPLETED'
        current.save()
        
    queue = get_queue(doctor, today)
    next_patient = next((a for a in queue if a.status == 'WAITING'), None)
    
    if next_patient:
        next_patient.status = 'CONSULTING'
        next_patient.save()
        
        Notification.objects.create(
            patient=next_patient.patient,
            message=f"🎫 YOUR TOKEN IS NOW BEING CALLED. Token: {next_patient.token_number}. Please proceed to the consultation room."
        )
        
    return redirect('doctor_dashboard')

@login_required
def complete_consultation(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, doctor__user=request.user)
    appt.status = 'COMPLETED'
    appt.save()
    return redirect('doctor_dashboard')

@login_required
def add_emergency(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        doctor_id = request.POST.get('doctor')
        
        if not patient_id:
            messages.error(request, "Select a patient")
            return redirect('add_emergency')
            
        patient = User.objects.get(id=patient_id)
        if hasattr(request.user, 'doctor'):
            doctor = request.user.doctor
        elif doctor_id:
            doctor = Doctor.objects.get(id=doctor_id)
        else:
            doctor = Doctor.objects.first()

        today = timezone.now().date()
        
        waiting_patients = Appointment.objects.filter(doctor=doctor, appointment_date=today, status='WAITING', priority='NORMAL')
        delay = doctor.average_consultation_minutes
        
        for p in waiting_patients:
            Notification.objects.create(
                patient=p.patient,
                message=f"🚨 DELAY NOTIFICATION: Emergency case detected for Dr. {doctor.name}. Your estimated waiting time has increased. Delay: +{delay} minutes."
            )
            
        appt = Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            appointment_date=today,
            appointment_time=timezone.now().time(),
            status='WAITING',
            priority='EMERGENCY',
            arrived_at=timezone.now(),
            token_number=generate_token(doctor, today)
        )
        messages.success(request, f"Emergency patient {patient.username} added for Dr. {doctor.name}. Token: {appt.token_number}")
        
        if hasattr(request.user, 'doctor'):
            return redirect('doctor_dashboard')
        elif request.user.is_staff or request.user.username == 'receptionist':
            return redirect('receptionist_dashboard')
        return redirect('home')
        
    patients = User.objects.filter(doctor__isnull=True, is_staff=False, is_superuser=False)
    doctors = Doctor.objects.filter(available=True)
    return render(request, 'emergency.html', {'patients': patients, 'doctors': doctors})

@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, patient=request.user)
    notif.is_read = True
    notif.save()
    return redirect('patient_dashboard')
