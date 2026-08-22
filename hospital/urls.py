from django.urls import path
from . import views

urlpatterns = [
    path("", views.public_home, name="home"),
    path("login/", views.login_view, name="login"),
    path("admin-login/", views.admin_login, name="admin_login"),
    path("doctor-login/", views.doctor_login, name="doctor_login"),
    path("patient-login/", views.patient_login, name="patient_login"),
    path("medical-login/", views.medical_login, name="medical_login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.patient_register, name="register"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("doctor-dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("medical-dashboard/", views.medical_dashboard, name="medical_dashboard"),
    path("patient-dashboard/", views.patient_dashboard, name="patient_dashboard"),

    path("doctor/patients/", views.doctor_patients, name="doctor_patients"),
    path("doctor/patient/<int:patient_id>/", views.doctor_patient_detail, name="doctor_patient_detail"),
    path("doctor-attendance/<str:status>/", views.doctor_mark_attendance, name="doctor_mark_attendance"),

    path("appointment/<int:pk>/confirm/", views.doctor_appointment_status, name="doctor_confirm", kwargs={"status":"Confirmed"}),
    path("appointment/<int:pk>/cancel/", views.doctor_appointment_status, name="doctor_cancel", kwargs={"status":"Cancelled"}),
    path("appointment/<int:pk>/complete/", views.doctor_complete, name="doctor_complete"),
    path("appointment/<int:appointment_id>/visit/", views.doctor_visit_register, name="doctor_visit_register"),
    path("appointment/<int:appointment_id>/record/", views.doctor_record, name="doctor_record"),
    path("appointment/<int:appointment_id>/prescription/", views.doctor_prescription, name="doctor_prescription"),

    path("medical/bill/add/", views.medical_create_bill, name="medical_create_bill"),
    path("medical/bill/<int:pk>/paid/", views.medical_mark_bill_paid, name="medical_mark_bill_paid"),

    path("patients/", views.patients, name="patients"),
    path("doctors/", views.doctors, name="doctors"),
    path("medical-staff/", views.medical_staff_list, name="medical_staff_list"),
    path("departments/", views.departments, name="departments"),
    path("appointments/", views.appointments, name="appointments"),
    path("attendance/", views.attendance, name="attendance"),
    path("records/", views.records, name="records"),
    path("prescriptions/", views.prescriptions, name="prescriptions"),
    path("bills/", views.bills, name="bills"),

    path("department/add/", views.add_department, name="add_department"),
    path("doctor/add/", views.add_doctor, name="add_doctor"),
    path("medical-staff/add/", views.add_medical_staff, name="add_medical_staff"),
    path("appointment/add/", views.add_admin_appointment, name="add_admin_appointment"),
    path("patient/appointment/book/", views.patient_book, name="patient_book"),
    path("appointment/<int:pk>/status/<str:status>/", views.appointment_status, name="appointment_status"),
]
