from flask import render_template, flash, request, Blueprint, redirect, url_for, abort
from .models import Patient, Appointment, Treatment, Availability
from . import db
from flask_login import current_user
from .forms import UpdateAppointmentForm, AvailabilityForm
from datetime import date, timedelta
from .decorators import doctor_required

doctor = Blueprint("doctor", __name__)


@doctor.route("/dashboard")
@doctor_required
def dashboard():
    if not current_user.is_authenticated or not hasattr(current_user, 'id'):
        return redirect(url_for('auth.login'))
    doctor_name = current_user.fname +" "+ current_user.lname
    upcoming_appointments = Appointment.query.filter_by(doctor_id=current_user.id,status='Booked').all()
    details=[]
    for appointment in upcoming_appointments:
        details.append({
            "id": appointment.id,
            "patient_fname": appointment.patient.fname,
            "patient_lname": appointment.patient.lname,
            "patient_id": appointment.patient_id,
        })
    assigned_patients_ids = Appointment.query.filter_by(doctor_id=current_user.id).with_entities(Appointment.patient_id).distinct().all()
    assigned_patients = []
    for id in assigned_patients_ids:
        patient = Patient.query.get(id.patient_id)
        assigned_patients.append({
            "id": patient.id,
            "fname": patient.fname,
            "lname": patient.lname,
        })

    return render_template("doctor/dashboard.html", name=doctor_name, appointments=details, assigned_patients=assigned_patients)

@doctor.route("/update/<appointment_id>", methods=['GET', 'POST'])
@doctor_required
def update_appointment_details(appointment_id):
    form = UpdateAppointmentForm()
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        # Updating appointment details
        if form.validate_on_submit():
            treatment = Treatment(
                appointment_id=appointment.id,
                visit_type=form.visit_type.data,
                tests_done=form.test_done.data,
                diagnosis=form.diagnosis.data,
                medicines=form.medicines.data,
                prescription=form.prescription.data
            )
            db.session.add(treatment)
            db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('doctor.dashboard'))
    return render_template("doctor/update.html", appointment=appointment, form=form)

@doctor.route("/patient_history/<int:patient_id>", methods=["GET"])
@doctor_required
def patient_history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
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
    return render_template("patient_details.html", title='Patient details', patient=patient, role="doctor", details=details)


@doctor.route("/update/<appointment_id>/<status>", methods=['POST'])
@doctor_required
def update_appointment_status(appointment_id, status):
    appointment = Appointment.query.get_or_404(appointment_id)
    if request.method == 'POST':
        if status == 'Completed':
            appointment.status = 'Completed'
            flash('Appointment status updated successfully!', 'success')
        elif status == 'Cancelled':
            appointment.status = 'Cancelled'
            flash('Appointment has been cancelled!', 'danger')
        db.session.commit()
        
        return redirect(url_for('doctor.dashboard'))
    return redirect(url_for('doctor.dashboard'))
    

"""
Providing avilability code wriiten is partly inspired by the official Flask scheduling examples
where i have taken a form made by wtf called Availabity form and used it to gain the availabilities provided by doc
if validateonsubmit part stands for psot request while elif stands for get 
if the get part i have taken the dates from today to next 7 days using datime library and that checking if it exist in db, if yess then sending those previously provid values, else just sending availability as true by default
"""

@doctor.route("/provide_availability", methods=["GET", "POST"])
@doctor_required
def provide_availability():
    form = AvailabilityForm()
    
    if form.validate_on_submit():
        # enumerate is something that python provides us help to ityerate and get index also i.e 'i', could have done it by simply using a i variable and incrementing over lop, but this is more pythonic
        for i, day_form in enumerate(form.days):
            current_date = date.today() + timedelta(days=i)
            
            availability = Availability.query.filter_by(
                doctor_id=current_user.id, 
                date=current_date
            ).first()
            if not availability:
                availability = Availability(
                    doctor_id=current_user.id, 
                    date=current_date
                )
            availability.morning_slot = day_form.morning_slot.data
            availability.evening_slot = day_form.evening_slot.data
                
            db.session.add(availability)
        
        db.session.commit()
        flash('Your availability has been updated!', 'success')
        return redirect(url_for('doctor.dashboard'))

    elif request.method == "GET":
        for i, day_form in enumerate(form.days):
            current_date = date.today() + timedelta(days=i)
            day_form.date_display.data = current_date.strftime('%d/%m/%Y')
            
            availability = Availability.query.filter_by(
                doctor_id=current_user.id, 
                date=current_date
            ).first()
            
            if availability:
                day_form.morning_slot.data = availability.morning_slot
                day_form.evening_slot.data = availability.evening_slot
                
    return render_template("doctor/provide_availability.html", title='Provide Availability', form=form)















