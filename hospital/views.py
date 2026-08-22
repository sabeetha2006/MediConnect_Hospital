from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError
from django import forms
from .models import *
from .forms import *

def role_required(role):
    def deco(view):
        @wraps(view)
        def wrapper(request,*args,**kwargs):
            if request.session.get("role") != role:
                messages.error(request,"Please login with the correct account.")
                return redirect("login")
            return view(request,*args,**kwargs)
        return wrapper
    return deco

def public_home(request):
    return render(request, "hospital/home.html")

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        # Hospital administrator account
        if username == "admin" and password == "admin123":
            request.session.flush()
            request.session["role"] = "admin"
            request.session["user_name"] = "Administrator"
            return redirect("admin_dashboard")

        # Staff / patient accounts
        candidates = [
            (Doctor, "doctor", "doctor_dashboard"),
            (Patient, "patient", "patient_dashboard"),
            (MedicalStaff, "medical", "medical_dashboard"),
        ]
        for Model, role, dashboard in candidates:
            qs = Model.objects.filter(username=username)
            if hasattr(Model, "is_active"):
                qs = qs.filter(is_active=True)
            obj = qs.first()
            if obj and obj.check_password(password):
                request.session.flush()
                request.session["role"] = role
                request.session["user_id"] = obj.id
                request.session["user_name"] = getattr(obj, "name", username)
                return redirect(dashboard)

        messages.error(request, "Invalid username or password.")
    return render(request, "hospital/login.html", {"form": form})

# Old role-specific URLs are kept for compatibility, but the UI uses one common login page.
def admin_login(request):
    return redirect("login")

def doctor_login(request):
    return redirect("login")

def patient_login(request):
    return redirect("login")

def medical_login(request):
    return redirect("login")

def logout_view(request):
    request.session.flush(); return redirect("home")

def patient_register(request):
    form = PatientRegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.username = form.cleaned_data["username"]
        obj.set_password(form.cleaned_data["password"])
        obj.save()
        messages.success(request, "Patient account created successfully. Please login.")
        return redirect("login")
    return render(request, "hospital/register.html", {"form": form})

@role_required("patient")
def patient_dashboard(request):
    patient=get_object_or_404(Patient,id=request.session["user_id"])
    return render(request,"hospital/patient_dashboard.html",{"patient":patient,"appointments":patient.appointments.select_related("doctor","doctor__department"),"records":patient.records.select_related("doctor"),"prescriptions":patient.prescriptions.select_related("doctor"),"bills":patient.bills.select_related("appointment","appointment__doctor"),"visits":DoctorPatientVisit.objects.filter(patient=patient).select_related("doctor")})

@role_required("patient")
def patient_book(request):
    patient=get_object_or_404(Patient,id=request.session["user_id"])
    form=AppointmentForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        a=form.save(commit=False); a.patient=patient; a.save()
        messages.success(request,"Appointment booked. Doctor must confirm it.")
        return redirect("patient_dashboard")
    return render(request,"hospital/form.html",{"form":form,"title":"Book Appointment","subtitle":"Choose an On Duty doctor and available slot.","back":"patient_dashboard"})

@role_required("doctor")
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    today = timezone.localdate()

    attendance = DoctorAttendance.objects.filter(
        doctor=doctor, attendance_date=today
    ).first()

    appointments = doctor.appointments.select_related(
        "patient", "doctor__department"
    ).order_by("appointment_date", "appointment_time")

    today_appointments = appointments.filter(
        appointment_date=today
    )

    upcoming_appointments = appointments.filter(
        appointment_date__gt=today
    ).order_by("appointment_date", "appointment_time")[:10]

    def workflow_row(appointment):
        has_visit = DoctorPatientVisit.objects.filter(
            appointment=appointment, doctor=doctor
        ).exists()
        has_record = MedicalRecord.objects.filter(
            appointment=appointment, doctor=doctor
        ).exists()
        has_prescription = Prescription.objects.filter(
            appointment=appointment, doctor=doctor
        ).exists()

        if appointment.status == "Pending":
            next_action = "Confirm"
        elif appointment.status == "Confirmed":
            if not has_visit:
                next_action = "Patient Check"
            elif not has_record:
                next_action = "Medical Report"
            elif not has_prescription:
                next_action = "Prescription"
            else:
                next_action = "Complete"
        elif appointment.status == "Completed":
            next_action = "Completed"
        else:
            next_action = "Cancelled"

        return {
            "appointment": appointment,
            "has_visit": has_visit,
            "has_record": has_record,
            "has_prescription": has_prescription,
            "next_action": next_action,
        }

    today_rows = [workflow_row(a) for a in today_appointments]
    upcoming_rows = [workflow_row(a) for a in upcoming_appointments]

    patient_ids = appointments.values_list(
        "patient_id", flat=True
    ).distinct()

    return render(request, "hospital/doctor_dashboard.html", {
        "doctor": doctor,
        "attendance": attendance,
        "today": today,
        "today_rows": today_rows,
        "upcoming_rows": upcoming_rows,
        "today_count": today_appointments.count(),
        "pending_count": appointments.filter(status="Pending").count(),
        "confirmed_count": appointments.filter(status="Confirmed").count(),
        "completed_count": appointments.filter(status="Completed").count(),
        "my_patients_count": patient_ids.count(),
    })


@role_required("doctor")
def doctor_patients(request):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    patient_ids = Appointment.objects.filter(
        doctor=doctor
    ).values_list("patient_id", flat=True).distinct()

    patients = Patient.objects.filter(
        id__in=patient_ids
    ).order_by("name")

    return render(request, "hospital/doctor_patients.html", {
        "doctor": doctor,
        "patients": patients,
    })


@role_required("doctor")
def doctor_mark_attendance(request, status):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    if status not in ["On Duty", "Off Duty"]:
        return redirect("doctor_dashboard")

    DoctorAttendance.objects.update_or_create(
        doctor=doctor,
        attendance_date=timezone.localdate(),
        defaults={"status": status},
    )
    messages.success(request, f"Attendance marked: {status}.")
    return redirect("doctor_dashboard")


@role_required("doctor")
def doctor_appointment_status(request, pk, status):
    doctor = get_object_or_404(
        Doctor, id=request.session["user_id"]
    )
    appointment = get_object_or_404(
        Appointment, pk=pk, doctor=doctor
    )

    if status == "Confirmed":
        if appointment.status != "Pending":
            messages.error(request, "Only pending appointments can be confirmed.")
            return redirect("doctor_dashboard")

        if appointment.appointment_date < timezone.localdate():
            messages.error(request, "Past appointments cannot be confirmed.")
            return redirect("doctor_dashboard")

        if not doctor.is_active:
            messages.error(request, "Your doctor account is currently inactive.")
            return redirect("doctor_dashboard")

        if appointment.appointment_date == timezone.localdate():
            on_duty = DoctorAttendance.objects.filter(
                doctor=doctor,
                attendance_date=appointment.appointment_date,
                status="On Duty",
            ).exists()
            if not on_duty:
                messages.error(
                    request,
                    "Please mark yourself On Duty before confirming today's appointment.",
                )
                return redirect("doctor_dashboard")

        appointment.status = "Confirmed"
        appointment.save(update_fields=["status"])
        messages.success(
            request,
            f"Appointment confirmed for {appointment.patient.name}. Now perform Patient Check.",
        )
        return redirect("doctor_patient_detail", patient_id=appointment.patient_id)

    if status == "Cancelled":
        if appointment.status not in ["Pending", "Confirmed"]:
            messages.error(request, "This appointment cannot be cancelled now.")
            return redirect("doctor_dashboard")

        appointment.status = "Cancelled"
        appointment.save(update_fields=["status"])
        messages.success(request, "Appointment cancelled.")
        return redirect("doctor_dashboard")

    return redirect("doctor_dashboard")


@role_required("doctor")
def doctor_complete(request, pk):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    appointment = get_object_or_404(
        Appointment, pk=pk, doctor=doctor
    )

    if appointment.status != "Confirmed":
        messages.error(request, "Only confirmed appointments can be completed.")
        return redirect("doctor_dashboard")

    # Consultation can be completed only after every workflow step is saved.
    has_visit = DoctorPatientVisit.objects.filter(
        appointment=appointment, doctor=doctor
    ).exists()
    has_record = MedicalRecord.objects.filter(
        appointment=appointment, doctor=doctor
    ).exists()
    has_prescription = Prescription.objects.filter(
        appointment=appointment, doctor=doctor
    ).exists()

    if not has_visit:
        messages.error(
            request,
            "Please complete Patient Check before completing the appointment.",
        )
        return redirect(
            "doctor_visit_register",
            appointment_id=appointment.id,
        )

    if not has_record:
        messages.error(
            request,
            "Please complete the Medical Report before completing the appointment.",
        )
        return redirect("doctor_record", appointment_id=appointment.id)

    if not has_prescription:
        messages.error(
            request,
            "Please add the Prescription before completing the appointment.",
        )
        return redirect("doctor_prescription", appointment_id=appointment.id)

    appointment.status = "Completed"
    appointment.save(update_fields=["status"])
    messages.success(request, "Consultation completed successfully.")
    return redirect("doctor_dashboard")


@role_required("doctor")
def doctor_patient_detail(request, patient_id):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])

    # Fetch the patient by primary key first. Using a reverse appointment
    # join with get_object_or_404() can return duplicate rows when the same
    # patient has multiple appointments with this doctor, causing
    # MultipleObjectsReturned.
    patient = get_object_or_404(Patient, id=patient_id)

    # A doctor may check only patients who have at least one appointment
    # with that doctor.
    if not Appointment.objects.filter(
        doctor=doctor, patient_id=patient.id
    ).exists():
        messages.error(request, "You are not authorized to view this patient.")
        return redirect("doctor_patients")

    appointments = Appointment.objects.filter(
        doctor=doctor, patient=patient
    ).select_related("doctor").order_by(
        "-appointment_date", "-appointment_time"
    )

    appointment_rows = []
    for appointment in appointments:
        appointment_rows.append({
            "appointment": appointment,
            "has_visit": DoctorPatientVisit.objects.filter(
                appointment=appointment
            ).exists(),
            "has_record": MedicalRecord.objects.filter(
                appointment=appointment, doctor=doctor
            ).exists(),
            "has_prescription": Prescription.objects.filter(
                appointment=appointment, doctor=doctor
            ).exists(),
        })

    records = MedicalRecord.objects.filter(
        doctor=doctor, patient=patient
    ).select_related("appointment").order_by("-record_date", "-id")

    prescriptions = Prescription.objects.filter(
        doctor=doctor, patient=patient
    ).select_related("appointment").order_by("-created_at")

    visits = DoctorPatientVisit.objects.filter(
        doctor=doctor, patient=patient
    ).order_by("-visit_date", "-id")

    return render(request, "hospital/doctor_patient_detail.html", {
        "doctor": doctor,
        "patient": patient,
        "appointments": appointments,
        "appointment_rows": appointment_rows,
        "records": records,
        "prescriptions": prescriptions,
        "visits": visits,
    })


@role_required("doctor")
def doctor_visit_register(request, appointment_id):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, doctor=doctor
    )

    if appointment.status != "Confirmed":
        messages.error(
            request,
            "Patient Check can be recorded only after the appointment is confirmed.",
        )
        return redirect("doctor_patient_detail", patient_id=appointment.patient_id)

    obj = DoctorPatientVisit.objects.filter(
        appointment=appointment
    ).first()

    form = DoctorPatientVisitForm(
        request.POST or None,
        instance=obj,
    )

    if request.method == "POST" and form.is_valid():
        visit = form.save(commit=False)
        visit.appointment = appointment
        visit.patient = appointment.patient
        visit.doctor = doctor
        visit.save()

        messages.success(
            request,
            "Patient Check saved. You can now create the Medical Report.",
        )
        return redirect(
            "doctor_record",
            appointment_id=appointment.id,
        )

    return render(request, "hospital/form.html", {
        "form": form,
        "title": "Patient Check",
        "subtitle": f"Check patient details before consultation: {appointment.patient.name}",
        "back": "doctor_patient_detail",
        "back_kwargs": {"patient_id": appointment.patient_id},
    })


@role_required("doctor")
def doctor_record(request, appointment_id):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, doctor=doctor
    )

    if appointment.status != "Confirmed":
        messages.error(
            request,
            "Medical Report can be added only for a confirmed appointment.",
        )
        return redirect("doctor_patient_detail", patient_id=appointment.patient_id)

    # Require Patient Check first.
    if not DoctorPatientVisit.objects.filter(
        appointment=appointment,
        doctor=doctor,
    ).exists():
        messages.error(
            request,
            "Please complete Patient Check first.",
        )
        return redirect(
            "doctor_visit_register",
            appointment_id=appointment.id,
        )

    obj = MedicalRecord.objects.filter(
        appointment=appointment,
        doctor=doctor,
    ).first()

    form = MedicalRecordForm(
        request.POST or None,
        instance=obj,
    )

    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.patient = appointment.patient
        record.doctor = doctor
        record.appointment = appointment
        record.save()

        messages.success(
            request,
            "Medical Report saved. You can now add the Prescription.",
        )
        return redirect(
            "doctor_prescription",
            appointment_id=appointment.id,
        )

    return render(request, "hospital/form.html", {
        "form": form,
        "title": "Medical Report",
        "subtitle": f"Consultation report for {appointment.patient.name}",
        "back": "doctor_patient_detail",
        "back_kwargs": {"patient_id": appointment.patient_id},
    })


@role_required("doctor")
def doctor_prescription(request, appointment_id):
    doctor = get_object_or_404(Doctor, id=request.session["user_id"])
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, doctor=doctor
    )

    if appointment.status != "Confirmed":
        messages.error(
            request,
            "Prescription can be added only for a confirmed appointment.",
        )
        return redirect("doctor_patient_detail", patient_id=appointment.patient_id)

    # Prescription is allowed only after Medical Report.
    if not MedicalRecord.objects.filter(
        appointment=appointment,
        doctor=doctor,
    ).exists():
        messages.error(
            request,
            "Please complete the Medical Report before adding a Prescription.",
        )
        return redirect(
            "doctor_record",
            appointment_id=appointment.id,
        )

    form = PrescriptionForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        prescription = form.save(commit=False)
        prescription.patient = appointment.patient
        prescription.doctor = doctor
        prescription.appointment = appointment
        prescription.save()

        messages.success(
            request,
            "Prescription saved successfully. Please click Complete Consultation.",
        )
        return redirect(
            "doctor_patient_detail",
            patient_id=appointment.patient_id,
        )

    return render(request, "hospital/form.html", {
        "form": form,
        "title": "Prescription",
        "subtitle": f"Prescription for {appointment.patient.name}",
        "back": "doctor_patient_detail",
        "back_kwargs": {"patient_id": appointment.patient_id},
    })


@role_required("medical")
def medical_dashboard(request):
    staff=get_object_or_404(MedicalStaff,id=request.session["user_id"])
    prescriptions=Prescription.objects.select_related("patient","doctor").order_by("-created_at")
    bills=Bill.objects.select_related("patient","appointment","appointment__doctor").order_by("-bill_date","-id")
    return render(request,"hospital/medical_dashboard.html",{"staff":staff,"prescriptions":prescriptions,"bills":bills,"pending_bills":bills.filter(payment_status="Pending").count(),"paid_bills":bills.filter(payment_status="Paid").count()})

@role_required("medical")
def medical_create_bill(request):
    form=MedicalBillForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        form.save(); messages.success(request,"Bill generated successfully."); return redirect("medical_dashboard")
    return render(request,"hospital/form.html",{"form":form,"title":"Generate Patient Bill","subtitle":"Create a bill and track payment status.","back":"medical_dashboard"})

@role_required("medical")
def medical_mark_bill_paid(request,pk):
    b=get_object_or_404(Bill,pk=pk); b.payment_status="Paid"; b.save(update_fields=["payment_status"]); messages.success(request,"Payment marked as Paid."); return redirect("medical_dashboard")

@role_required("admin")
def admin_dashboard(request):
    today=timezone.localdate()
    return render(request,"hospital/admin_dashboard.html",{"patients":Patient.objects.all().order_by("-id"),"doctors":Doctor.objects.select_related("department"),"staff":MedicalStaff.objects.all(),"appointments":Appointment.objects.select_related("patient","doctor").order_by("-appointment_date","-appointment_time"),"attendance":DoctorAttendance.objects.select_related("doctor").filter(attendance_date=today),"bills":Bill.objects.select_related("patient","appointment","appointment__doctor").order_by("-id"),"departments":Department.objects.all()})

# Admin list/create helpers
@role_required("admin")
def patients(request): return render(request,"hospital/patients.html",{"patients":Patient.objects.all()})
@role_required("admin")
def doctors(request): return render(request,"hospital/doctors.html",{"doctors":Doctor.objects.select_related("department")})
@role_required("admin")
def medical_staff_list(request): return render(request,"hospital/medical_staff.html",{"staff":MedicalStaff.objects.all()})
@role_required("admin")
def departments(request): return render(request,"hospital/departments.html",{"departments":Department.objects.all()})
@role_required("admin")
def appointments(request): return render(request,"hospital/appointments.html",{"appointments":Appointment.objects.select_related("patient","doctor")})
@role_required("admin")
def attendance(request): return render(request,"hospital/attendance.html",{"attendance":DoctorAttendance.objects.select_related("doctor").order_by("-attendance_date","doctor__name")})
@role_required("admin")
def records(request): return render(request,"hospital/records.html",{"records":MedicalRecord.objects.select_related("patient","doctor")})
@role_required("admin")
def prescriptions(request): return render(request,"hospital/prescriptions.html",{"prescriptions":Prescription.objects.select_related("patient","doctor")})
@role_required("admin")
def bills(request): return render(request,"hospital/bills.html",{"bills":Bill.objects.select_related("patient","appointment","appointment__doctor")})

@role_required("admin")
def add_department(request):
    form=DepartmentForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Department added."); return redirect("departments")
    return render(request,"hospital/form.html",{"form":form,"title":"Add Department","subtitle":"Create a hospital department.","back":"admin_dashboard"})

@role_required("admin")
def add_doctor(request):
    form=DoctorForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Doctor added."); return redirect("doctors")
    return render(request,"hospital/form.html",{"form":form,"title":"Add Doctor","subtitle":"Create doctor login and profile.","back":"admin_dashboard"})

@role_required("admin")
def add_medical_staff(request):
    form=MedicalStaffForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Medical staff added."); return redirect("medical_staff_list")
    return render(request,"hospital/form.html",{"form":form,"title":"Add Medical Staff","subtitle":"Create medical staff login.","back":"admin_dashboard"})

@role_required("admin")
def add_admin_appointment(request):
    class AdminAppointmentForm(StyledModelForm):
        class Meta:
            model=Appointment; fields=["patient","doctor","appointment_date","appointment_time","reason","status"]
            widgets={"appointment_date":forms.DateInput(attrs={"type":"date"}),"appointment_time":forms.TimeInput(attrs={"type":"time"}),"reason":forms.Textarea(attrs={"rows":3})}
    form=AdminAppointmentForm(request.POST or None)
    if request.method=="POST" and form.is_valid(): form.save(); messages.success(request,"Appointment added."); return redirect("appointments")
    return render(request,"hospital/form.html",{"form":form,"title":"Add Appointment","subtitle":"Create an appointment from admin.","back":"admin_dashboard"})

@role_required("admin")
def appointment_status(request,pk,status):
    a=get_object_or_404(Appointment,pk=pk)
    if status in dict(Appointment.STATUS): a.status=status; a.save(update_fields=["status"])
    return redirect("appointments")
