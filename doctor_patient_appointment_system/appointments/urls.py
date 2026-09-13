from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Common URLs
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.patient_login, name='login'),
    path('patient/login/', views.patient_login, name='patient_login'),
    path('receptionist/login/', views.receptionist_login, name='receptionist_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    # Patient URLs
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/book/', views.patient_book, name='patient_book'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/tracking/', views.patient_tracking, name='patient_tracking'),
    path('patient/notifications/', views.patient_notifications, name='patient_notifications'),
    path('patient/notifications/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),

    # Receptionist URLs (Only 5 Pages + 1-click POST handlers)
    path('receptionist/dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('receptionist/appointments/', views.receptionist_appointments, name='receptionist_appointments'),
    path('receptionist/complete/<int:appt_id>/', views.complete_appointment_action, name='complete_appointment_action'),
    path('receptionist/queue/', views.receptionist_queue, name='receptionist_queue'),
    path('receptionist/emergency/<int:appt_id>/', views.mark_emergency_action, name='mark_emergency_action'),
    path('receptionist/delay/', views.receptionist_delay, name='receptionist_delay'),
    path('receptionist/delay/apply/', views.apply_delay_action, name='apply_delay_action'),
    path('receptionist/management/', views.receptionist_management, name='receptionist_management'),
]
