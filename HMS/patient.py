from flask import render_template, flash, request, Blueprint, redirect, url_for
from .models import Patient, Doctor, Appointment, Treatment, Department, Availability
from . import db
from flask_login import current_user
from .forms import PatientProfileEditForm, BookAppointmentForm
from datetime import date, timedelta, time
from .decorators import  patient_required

patient = Blueprint("patient", __name__)

@patient.route("/dashboard")
@patient_required
def dashboard():
    if not current_user.is_authenticated or not hasattr(current_user, 'id'):
        return redirect(url_for('auth.login'))
    departments = Department.query.all()
    appointments = Appointment.query.filter_by(patient_id=current_user.id, status="Booked").all()
    cancelled_appointments = Appointment.query.filter_by(patient_id=current_user.id, status="Cancelled").all()
    return render_template("patient/dashboard.html", user=current_user, departments=departments, appointments=appointments, cancelled_appointments=cancelled_appointments)


@patient.route("/edit_profile/<int:patient_id>", methods=["GET", "POST"])
@patient_required
def edit_profile(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientProfileEditForm(patient_to_update=patient)
    
    if form.validate_on_submit():
        patient.fname = form.fname.data
        patient.lname = form.lname.data
        patient.email = form.email.data
        patient.phone = form.phone.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        db.session.commit()
        flash('Patient profile updated successfully!', 'success')
        return redirect(url_for('patient.dashboard'))

    elif request.method == "GET":
        form.fname.data = patient.fname
        form.lname.data = patient.lname
        form.email.data = patient.email
        form.phone.data = patient.phone
        form.age.data = patient.age
        form.gender.data = patient.gender.lower()

    return render_template("admin/edit_patient_profile.html", role="patient", title='Update Patient', patient=patient, form=form)

@patient.route("/history/<int:patient_id>", methods=["GET"])
@patient_required
def view_history(patient_id):
    patient_id = current_user.id
    appointment_ids = Appointment.query.filter_by(patient_id=patient_id).all()
    details = []
    for record in appointment_ids:
        treatment = Treatment.query.filter_by(appointment_id=record.id).first()
        if treatment:
            details.append({
                "visit_type": treatment.visit_type ,
                "diagnosis": treatment.diagnosis ,
                "tests_done": treatment.tests_done ,
                "prescription": treatment.prescription ,
                "medicines": treatment.medicines
            })
    return render_template("history.html", title='View Patient', patient_id=patient_id,  role="patient", details=details)



@patient.route("/dept_view/<int:department_id>", methods=["GET"])
@patient_required
def view_department(department_id):
    department = Department.query.get_or_404(department_id)
    doctors = Doctor.query.filter_by(specialization_id=department.id).all()
    return render_template("patient/view_department.html", department=department, doctors=doctors)


@patient.route("/<int:appointment_id>", methods=["POST"])
@patient_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != current_user.id:
        flash("You do not have permission to cancel this appointment.", "danger")
        return redirect(url_for("patient.dashboard"))
    
    appointment.status = "Cancelled"
    db.session.commit()
    flash("Appointment cancelled successfully.", "success")
    return redirect(url_for("patient.dashboard"))


@patient.route("/view-doctor/<int:id>", methods=["GET"])
def view_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    return render_template("doctor_details.html", title="Doctor Details", doctor=doctor, role="patient")


"""
Function to allow patient to view and reserve an available slot with a doctor.
slot_options contains the available slots of next 7 days and slots are taken from database where moening and evening slots are marked true/false
throughout this loop i crated slot option and used those slots as option in my form select field
next i have splitted the selected slot to get date and time period and created appointment accordingly and updated availability table to mark that slot as booked
"""

@patient.route("/book-appointment/<int:doctor_id>", methods=["GET", "POST"])
@patient_required
def book_appointment(doctor_id):

    doctor = Doctor.query.get_or_404(doctor_id)
    form = BookAppointmentForm()
    today = date.today()

    # Building a list of available slots for the next 7 days 
    slot_options = []
    for offset in range(7):
        day = today + timedelta(days=offset)
        record = Availability.query.filter_by(doctor_id=doctor.id, date=day).first()

        timeframes = [
            ("morning", "08:00 AM - 12:00 PM"),
            ("evening", "04:00 PM - 09:00 PM")
        ]

        for period, label_time in timeframes:
            slot_open = True
            if record:
                if period == "morning":
                    slot_open = record.morning_slot
                elif period == "evening":
                    slot_open = record.evening_slot

            if slot_open:
                value_key = f"{day.isoformat()}_{period}"
                label_text = f"{day.strftime('%A, %b %d')} — {period.title()} ({label_time})"
                slot_options.append((value_key, label_text))

    form.slot.choices = slot_options

    if form.validate_on_submit():
        try:
            date_part, period = form.slot.data.split("_")
            selected_date = date.fromisoformat(date_part)
            selected_time = time(8, 0, 0) if period == "morning" else time(16, 0, 0)

            appointment = Appointment(
                doctor_id=doctor.id,
                patient_id=current_user.id,
                date=selected_date,
                time=selected_time,
                status="Booked"
            )

            availability = Availability.query.filter_by(
                doctor_id=doctor.id, date=selected_date
            ).first()

            if availability:
                if period == "morning":
                    availability.morning_slot = False
                elif period == "evening":
                    availability.evening_slot = False
            else:
                availability = Availability(
                    doctor_id=doctor.id,
                    date=selected_date,
                    morning_slot=(period != "morning"),
                    evening_slot=(period != "evening")
                )
                db.session.add(availability)

            db.session.add(appointment)
            db.session.commit()

            flash("Your appointment has been successfully booked.", "success")
            return redirect(url_for("patient.view_department", department_id=doctor.specialization_id))

        except Exception as e:
            db.session.rollback()
            flash("An unexpected error occurred while booking the appointment.", "danger")

    return render_template(
        "patient/book_appointment.html",
        title="Book Appointment",
        form=form,
        doctor=doctor
    )
