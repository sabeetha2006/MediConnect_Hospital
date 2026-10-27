# MediConnect Hospital Management System

Django 4.2 hospital management project with separate workflows for Admin, Doctor, Patient and Medical Staff.

## Run

```cmd
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python seed_demo.py
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Login

The website has one common login page. Demo credentials are intentionally **not displayed on the login screen**.

- Admin: `admin` / `admin123`
- Doctor: `doctor1` / `doctor123`
- Patient: `patient1` / `patient123`
- Medical: `medical1` / `medical123`

## Main workflows

### Admin
- Sidebar: Doctors, Patients, Attendance, Appointments, Prescriptions, Bills, Logout
- Add doctors, medical staff, departments and admin appointments
- Monitor attendance, appointments, records, prescriptions and bills

### Doctor
- On Duty / Off Duty
- Today's and upcoming appointments
- Patient Check page with patient profile and previous records/prescriptions
- Confirm / Cancel appointments
- Patient Visit details
- Medical Record: symptoms, diagnosis, vitals, treatment and follow-up
- Prescription: medicine, dosage, duration and instructions
- Complete consultation
- Logout

### Patient
- Register as a new patient
- Book appointments
- Track appointment status
- View medical records, prescriptions, bills and consultation details
- Logout

### Medical Staff
- View doctor prescriptions
- View medical records
- Generate patient bills
- Mark pending bills as Paid
- Logout

## Important

If an older project folder already contains `db.sqlite3`, run `python manage.py migrate` first. If the database is from an incompatible older version, delete `db.sqlite3`, run `python manage.py migrate`, then run `python seed_demo.py`.
<!-- python manage.py runserver -->