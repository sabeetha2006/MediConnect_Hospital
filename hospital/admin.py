from django.contrib import admin
from .models import *
admin.site.register([Department,Patient,Doctor,MedicalStaff,DoctorAttendance,Appointment,DoctorPatientVisit,MedicalRecord,Prescription,Bill])
