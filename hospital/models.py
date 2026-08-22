from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class LoginMixin(models.Model):
    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=128)
    class Meta:
        abstract = True
    def set_password(self, raw):
        self.password = make_password(raw)
    def check_password(self, raw):
        return check_password(raw, self.password)

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    def __str__(self): return self.name

class Patient(LoginMixin):
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    blood_group = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Doctor(LoginMixin):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120)
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    experience = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    def __str__(self): return f"Dr. {self.name}"

class MedicalStaff(LoginMixin):
    name = models.CharField(max_length=120)
    designation = models.CharField(max_length=100, default="Medical Staff")
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

class DoctorAttendance(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    attendance_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=[("On Duty","On Duty"),("Off Duty","Off Duty")])
    marked_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["doctor","attendance_date"], name="unique_doctor_day")]
    def __str__(self): return f"{self.doctor} - {self.attendance_date} - {self.status}"

class Appointment(models.Model):
    STATUS = [("Pending","Pending"),("Confirmed","Confirmed"),("Cancelled","Cancelled"),("Completed","Completed")]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.patient} - {self.doctor} - {self.appointment_date}"

class DoctorPatientVisit(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="visit")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    visit_date = models.DateField(default=timezone.localdate)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    blood_pressure = models.CharField(max_length=30, blank=True)
    temperature = models.CharField(max_length=30, blank=True)
    weight = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True)

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="records")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.SET_NULL)
    record_date = models.DateField(default=timezone.localdate)
    symptoms = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    blood_pressure = models.CharField(max_length=30, blank=True)
    temperature = models.CharField(max_length=30, blank=True)
    weight = models.CharField(max_length=30, blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, null=True, blank=True, on_delete=models.SET_NULL)
    medicine = models.CharField(max_length=160)
    dosage = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Bill(models.Model):
    PAYMENT = [("Pending","Pending"),("Paid","Paid")]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="bills")
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name="bill")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT, default="Pending")
    bill_date = models.DateField(default=timezone.localdate)
    @property
    def total(self):
        return self.consultation_fee + self.medicine_fee + self.lab_fee + self.other_fee
