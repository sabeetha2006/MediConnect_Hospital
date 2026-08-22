from django import forms
from django.utils import timezone
from .models import Patient, Department, Doctor, Appointment, MedicalRecord, Prescription, Bill, DoctorPatientVisit, MedicalStaff, DoctorAttendance

class StyledModelForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class","form-control")

class PatientRegisterForm(StyledModelForm):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Choose username"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Create password"}))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Confirm password"}))
    class Meta:
        model=Patient
        fields=["name","age","gender","phone","email","address","blood_group"]
        widgets={"name":forms.TextInput(attrs={"placeholder":"Full name"}),"age":forms.NumberInput(attrs={"min":1,"max":120,"placeholder":"Age"}),"phone":forms.TextInput(attrs={"placeholder":"10-digit phone"}),"email":forms.EmailInput(attrs={"placeholder":"Email address"}),"address":forms.Textarea(attrs={"rows":3,"placeholder":"Address"}),"blood_group":forms.TextInput(attrs={"placeholder":"e.g. O+"})}
    def clean(self):
        data=super().clean()
        if data.get("password") != data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match.")
        if Patient.objects.filter(username=data.get("username")).exists():
            raise forms.ValidationError("Username already exists.")
        return data

class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput(attrs={"class":"form-control","placeholder":"Username"}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={"class":"form-control","placeholder":"Password"}))

class DepartmentForm(StyledModelForm):
    class Meta:
        model=Department; fields=["name","description"]
        widgets={"description":forms.Textarea(attrs={"rows":3})}

class DoctorForm(StyledModelForm):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=Doctor; fields=["name","specialization","department","phone","email","experience"]
    def save(self,commit=True):
        obj=super().save(commit=False); obj.username=self.cleaned_data["username"]; obj.set_password(self.cleaned_data["password"])
        if commit: obj.save()
        return obj

class MedicalStaffForm(StyledModelForm):
    username=forms.CharField()
    password=forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model=MedicalStaff; fields=["name","designation","phone","email"]
    def save(self,commit=True):
        obj=super().save(commit=False); obj.username=self.cleaned_data["username"]; obj.set_password(self.cleaned_data["password"])
        if commit: obj.save()
        return obj

class AppointmentForm(StyledModelForm):
    class Meta:
        model=Appointment; fields=["doctor","appointment_date","appointment_time","reason"]
        widgets={"appointment_date":forms.DateInput(attrs={"type":"date"}),"appointment_time":forms.TimeInput(attrs={"type":"time"}),"reason":forms.Textarea(attrs={"rows":3,"placeholder":"Reason for visit"})}
    def clean(self):
        data=super().clean(); doctor=data.get("doctor"); date=data.get("appointment_date"); time=data.get("appointment_time")
        if date and date < timezone.localdate(): raise forms.ValidationError("Choose today or a future date.")
        if doctor and date and time and Appointment.objects.filter(doctor=doctor,appointment_date=date,appointment_time=time,status__in=["Pending","Confirmed"]).exists():
            raise forms.ValidationError("This doctor already has an active appointment at that time.")
        if doctor and not doctor.is_active:
            raise forms.ValidationError("This doctor is currently unavailable.")
        return data

class DoctorPatientVisitForm(StyledModelForm):
    class Meta:
        model=DoctorPatientVisit
        fields=["visit_date","symptoms","diagnosis","blood_pressure","temperature","weight","notes"]
        widgets={"visit_date":forms.DateInput(attrs={"type":"date"}),"symptoms":forms.Textarea(attrs={"rows":3}),"diagnosis":forms.Textarea(attrs={"rows":3}),"notes":forms.Textarea(attrs={"rows":3})}

class MedicalRecordForm(StyledModelForm):
    class Meta:
        model=MedicalRecord
        fields=["symptoms","diagnosis","blood_pressure","temperature","weight","treatment_plan","follow_up_date","notes"]
        widgets={"symptoms":forms.Textarea(attrs={"rows":3}),"diagnosis":forms.Textarea(attrs={"rows":3}),"treatment_plan":forms.Textarea(attrs={"rows":3}),"follow_up_date":forms.DateInput(attrs={"type":"date"}),"notes":forms.Textarea(attrs={"rows":3})}

class PrescriptionForm(StyledModelForm):
    class Meta:
        model=Prescription
        fields=["medicine","dosage","duration","instructions"]
        widgets={"instructions":forms.Textarea(attrs={"rows":3})}

class MedicalBillForm(StyledModelForm):
    class Meta:
        model=Bill
        fields=["patient","appointment","consultation_fee","medicine_fee","lab_fee","other_fee","payment_status"]
        widgets={"consultation_fee":forms.NumberInput(attrs={"min":"0","step":"0.01"}),"medicine_fee":forms.NumberInput(attrs={"min":"0","step":"0.01"}),"lab_fee":forms.NumberInput(attrs={"min":"0","step":"0.01"}),"other_fee":forms.NumberInput(attrs={"min":"0","step":"0.01"})}
    def clean(self):
        data=super().clean(); patient=data.get("patient"); appointment=data.get("appointment")
        if patient and appointment and appointment.patient_id != patient.id: raise forms.ValidationError("Selected appointment does not belong to selected patient.")
        if appointment and Bill.objects.filter(appointment=appointment).exists(): raise forms.ValidationError("A bill already exists for this appointment.")
        return data
