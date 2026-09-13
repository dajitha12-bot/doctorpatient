
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # Patient URLs
    path('doctors/', views.doctors_list, name='doctors_list'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('check_in/<int:appt_id>/', views.check_in, name='check_in'),
    path('api/patient_queue_status/', views.patient_queue_status, name='patient_queue_status'),
    path('notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    
    # Doctor URLs
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('call_next/', views.call_next_patient, name='call_next'),
    path('complete_consultation/<int:appt_id>/', views.complete_consultation, name='complete_consultation'),
    path('add_emergency/', views.add_emergency, name='add_emergency'),
    
    # Receptionist / Admin URLs
    path('receptionist_dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('receptionist_check_in/<int:appt_id>/', views.receptionist_check_in, name='receptionist_check_in'),
]
