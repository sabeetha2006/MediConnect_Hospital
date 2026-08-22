import os
from datetime import timedelta, time
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospital_management.settings")
import django
django.setup()
from django.utils import timezone
from hospital.models import Department, Doctor, MedicalStaff, Patient, DoctorAttendance, Appointment, DoctorPatientVisit, MedicalRecord, Prescription, Bill

d,_ = Department.objects.get_or_create(
    name="General Medicine",
    defaults={"description":"General medical care"}
)

def add(model, username, password, **kw):
    obj = model.objects.filter(username=username).first()
    if not obj:
        obj = model(username=username, **kw)
        obj.set_password(password)
        obj.save()
    return obj

doctor = add(Doctor, "doctor1", "doctor123", name="Arun Kumar", specialization="General Physician", department=d, phone="9876543210", email="doctor@mediconnect.com", experience=8)
staff = add(MedicalStaff, "medical1", "medical123", name="Meena", designation="Medical Staff", phone="9876501234", email="medical@mediconnect.com")
patient = add(Patient, "patient1", "patient123", name="Demo Patient", age=22, gender="Female", phone="9876543201", email="patient@mediconnect.com", address="Chennai", blood_group="O+")

today = timezone.localdate()
DoctorAttendance.objects.update_or_create(doctor=doctor, attendance_date=today, defaults={"status":"On Duty"})

# One today's pending appointment so the doctor portal is immediately testable.
a, created = Appointment.objects.get_or_create(
    patient=patient, doctor=doctor, appointment_date=today, appointment_time=time(10, 30),
    defaults={"reason":"Fever and general consultation", "status":"Pending"}
)

# One upcoming appointment for testing the upcoming section.
Appointment.objects.get_or_create(
    patient=patient, doctor=doctor, appointment_date=today + timedelta(days=7), appointment_time=time(14, 0),
    defaults={"reason":"Follow-up consultation", "status":"Pending"}
)

print("Demo data ready.")
print("Admin: admin / admin123")
print("Doctor: doctor1 / doctor123")
print("Patient: patient1 / patient123")
print("Medical: medical1 / medical123")
