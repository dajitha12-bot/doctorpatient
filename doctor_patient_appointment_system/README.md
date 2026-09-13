# Doctor-Patient Appointment Tracking System

A simple Django web application designed for hospital queue tracking with emergency management.

## Pre-Configured Demo Accounts for All 3 User Roles

### 1. Receptionist / Admin Role
- **Username:** `receptionist`
- **Password:** `receptionist123`
- **Capabilities:** System stats, patient check-in control, add emergency patients, monitor doctor queues, Django Admin access (`/admin/`).

### 2. Doctor Role
- **Cardiology Doctor Username:** `dr_arun`
- **Neurology Doctor Username:** `dr_priya`
- **Orthopedics Doctor Username:** `dr_rajesh`
- **Password for all doctors:** `doctor123`
- **Capabilities:** View today's queue, call next patient, complete consultation, add emergency patient.

### 3. Patient Role
- **Patient Username:** `patient1` (or `patient2`, `patient3`)
- **Password for all patients:** `patient123`
- **Capabilities:** Search doctors, book appointments, check-in, live token tracking, view delay notifications.

## Windows Setup & Run Instructions

1. **Open Command Prompt or PowerShell**.
2. **Navigate** to this folder (the folder containing `manage.py`).
3. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run Migrations & Seed Data**:
   ```bash
   python manage.py makemigrations
   python manage.py makemigrations appointments
   python manage.py migrate
   python manage.py populate_doctors
   ```
6. **Start the Server**:
   ```bash
   python manage.py runserver
   ```
7. Visit `http://127.0.0.1:8000/` and log in with any of the demo accounts!
