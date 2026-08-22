# Generated manually for MediConnect Hospital
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Patient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=80, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("name", models.CharField(max_length=120)),
                ("age", models.PositiveIntegerField()),
                ("gender", models.CharField(max_length=20)),
                ("phone", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("address", models.TextField()),
                ("blood_group", models.CharField(blank=True, max_length=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={},
        ),
        migrations.CreateModel(
            name="Doctor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=80, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("name", models.CharField(max_length=120)),
                ("specialization", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("experience", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="hospital.department")),
            ],
        ),
        migrations.CreateModel(
            name="MedicalStaff",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("username", models.CharField(max_length=80, unique=True)),
                ("password", models.CharField(max_length=128)),
                ("name", models.CharField(max_length=120)),
                ("designation", models.CharField(default="Medical Staff", max_length=100)),
                ("phone", models.CharField(max_length=15)),
                ("email", models.EmailField(max_length=254)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Appointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("appointment_date", models.DateField()),
                ("appointment_time", models.TimeField()),
                ("reason", models.TextField()),
                ("status", models.CharField(choices=[("Pending","Pending"),("Confirmed","Confirmed"),("Cancelled","Cancelled"),("Completed","Completed")], default="Pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to="hospital.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="appointments", to="hospital.patient")),
            ],
        ),
        migrations.CreateModel(
            name="DoctorAttendance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("attendance_date", models.DateField(default=django.utils.timezone.localdate)),
                ("status", models.CharField(choices=[("On Duty","On Duty"),("Off Duty","Off Duty")], max_length=20)),
                ("marked_at", models.DateTimeField(auto_now=True)),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hospital.doctor")),
            ],
            options={"constraints":[models.UniqueConstraint(fields=("doctor","attendance_date"), name="unique_doctor_day")]},
        ),
        migrations.CreateModel(
            name="DoctorPatientVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("visit_date", models.DateField(default=django.utils.timezone.localdate)),
                ("symptoms", models.TextField(blank=True)),
                ("diagnosis", models.TextField(blank=True)),
                ("blood_pressure", models.CharField(blank=True, max_length=30)),
                ("temperature", models.CharField(blank=True, max_length=30)),
                ("weight", models.CharField(blank=True, max_length=30)),
                ("notes", models.TextField(blank=True)),
                ("appointment", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="visit", to="hospital.appointment")),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hospital.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hospital.patient")),
            ],
        ),
        migrations.CreateModel(
            name="MedicalRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("record_date", models.DateField(default=django.utils.timezone.localdate)),
                ("symptoms", models.TextField(blank=True)),
                ("diagnosis", models.TextField(blank=True)),
                ("blood_pressure", models.CharField(blank=True, max_length=30)),
                ("temperature", models.CharField(blank=True, max_length=30)),
                ("weight", models.CharField(blank=True, max_length=30)),
                ("treatment_plan", models.TextField(blank=True)),
                ("follow_up_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("appointment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="hospital.appointment")),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hospital.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="records", to="hospital.patient")),
            ],
        ),
        migrations.CreateModel(
            name="Prescription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("medicine", models.CharField(max_length=160)),
                ("dosage", models.CharField(max_length=100)),
                ("duration", models.CharField(max_length=100)),
                ("instructions", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("appointment", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="hospital.appointment")),
                ("doctor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="hospital.doctor")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prescriptions", to="hospital.patient")),
            ],
        ),
        migrations.CreateModel(
            name="Bill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("consultation_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("medicine_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("lab_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("other_fee", models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ("payment_status", models.CharField(choices=[("Pending","Pending"),("Paid","Paid")], default="Pending", max_length=20)),
                ("bill_date", models.DateField(default=django.utils.timezone.localdate)),
                ("appointment", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="bill", to="hospital.appointment")),
                ("patient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bills", to="hospital.patient")),
            ],
        ),
    ]
