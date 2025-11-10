from flask import render_template, flash, request, Blueprint, redirect, url_for
from .models import Patient, Doctor, Admin, Appointment, Treatment, Department
from .forms import  AdminLoginForm, RegisterDoctorForm, PatientProfileEditForm, DoctorProfileEditForm, SearchForm
from . import db, bcrypt
from flask_login import login_user, current_user, logout_user
from sqlalchemy import or_
from .decorators import admin_required

# Admin login 
admin = Blueprint("admin", __name__)
@admin.route("/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
            admin = Admin.query.filter_by(email=form.email.data).first()
            if admin and bcrypt.check_password_hash(admin.password, form.password.data):
                login_user(admin, remember=form.remember.data)

                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("admin.dashboard"))

            else:
                flash("Login Unsuccessful. Please check email and password", "danger")
            
    return render_template("admin/login.html", title='Login', form=form)

# admin dahboard that has all the patients and doctor and upcoming and previous appointment details 
@admin.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    form = SearchForm()
    appointments = Appointment.query.all()
    upcoming_details = []
    previous_details = []
    for appointment in appointments:
        if appointment.status == "Booked":
            upcoming_details.append({
                "id": appointment.id,
                'patient_id': appointment.patient_id,
                "patient_name": appointment.patient.fname + " " + appointment.patient.lname,
                "doctor_name": appointment.doctor.fname + " " + appointment.doctor.lname,
                "department": appointment.doctor.specialization.name
            })
        else:
            previous_details.append({
                "id": appointment.id,
                'patient_id': appointment.patient_id,
                "patient_name": appointment.patient.fname + " " + appointment.patient.lname,
                "doctor_name": appointment.doctor.fname + " " + appointment.doctor.lname,
                "department": appointment.doctor.specialization.name
            })

    patients = Patient.query.all()
    doctors = Doctor.query.all()
    return render_template("admin/dashboard.html", title='Dashboard', upcoming_details=upcoming_details, previous_details=previous_details, patients=patients, doctors=doctors, form=form)


# Admin route to register a new doctor
@admin.route('/register-doctor', methods=['GET', 'POST'])
@admin_required
def register_doctor():
    form = RegisterDoctorForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        doctor = Doctor(
            fname=form.fname.data,
            lname=form.lname.data,
            email=form.email.data,
            phone=form.phone.data,
            password=hashed_password,
            specialization_id=form.specialization_id.data,
            experience=form.experience.data,
            description=form.description.data
        )

        db.session.add(doctor)
        db.session.commit()
        flash('Doctor has been registered successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template("admin/register_doctor.html", title='Register Doctor', form=form)


# to look at the history of ppatient 
@admin.route("/view/<int:appointment_id>", methods=["GET"])
@admin_required
def view(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    patient_id = appointment.patient_id
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
    return render_template("history.html", title='View Patient', patient_id=patient_id, appointment=appointment, role="admin", details=details)


# admin can also update patient details
@admin.route("/update_patient/<int:patient_id>", methods=["GET", "POST"])
@admin_required
def update_patient(patient_id):
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
        return redirect(url_for('admin.dashboard'))

    elif request.method == "GET":
        form.fname.data = patient.fname
        form.lname.data = patient.lname
        form.email.data = patient.email
        form.phone.data = patient.phone
        form.age.data = patient.age
        form.gender.data = patient.gender.lower()

    return render_template("admin/edit_patient_profile.html", title='Update Patient', role="admin", patient=patient, form=form)

# admin can also update doctor details
@admin.route("/update_doctor/<int:doctor_id>", methods=["GET", 'POST'])
@admin_required
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    form = DoctorProfileEditForm(doctor_to_update=doctor)
    
    if form.validate_on_submit():
        doctor.fname = form.fname.data
        doctor.lname = form.lname.data
        doctor.email = form.email.data
        doctor.phone = form.phone.data
        doctor.experience = form.experience.data
        doctor.specialization_id = form.specialization_id.data
        doctor.description = form.description.data
        db.session.commit()
        flash('Doctor profile updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    elif request.method == "GET":
        form.fname.data = doctor.fname
        form.lname.data = doctor.lname
        form.email.data = doctor.email
        form.phone.data = doctor.phone
        form.experience.data = doctor.experience
        form.specialization_id.data = doctor.specialization_id
        form.description.data = doctor.description

    return render_template("admin/edit_doctor_profile.html", title='Update Doctor', doctor=doctor, form=form)

# route to blaclist the doctor and patient which take role and id as parameter
@admin.route("/blacklist/<role>/<int:id>", methods=["GET", 'POST'])
@admin_required
def blacklist(role, id):
    if role == "doctor":
        user = Doctor.query.get_or_404(id)
    elif role == "patient":
        user = Patient.query.get_or_404(id)
    else:
        flash("Invalid role specified.", "danger")
        return redirect(url_for("admin.dashboard"))

    user.blacklisted = not user.blacklisted
    status = "blacklisted" if user.blacklisted else "removed from blacklist"
    db.session.commit()
    flash(f"{role.capitalize()} has been {status} successfully!", "success")
    return redirect(url_for("admin.dashboard"))

# delete route to delete doctor and patient based on role and id
@admin.route("/delete/<role>/<int:id>", methods=["GET", 'POST'])
@admin_required
def delete(role, id):
    if role == "doctor":
        user = Doctor.query.get_or_404(id)
    elif role == "patient":
        user = Patient.query.get_or_404(id)
    else:
        flash("Invalid role specified.", "danger")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(user)
    db.session.commit()
    flash(f"{role.capitalize()} has been deleted successfully!", "success")
    return redirect(url_for("admin.dashboard"))

# seach take searchform for get request and when posted gives a value where i have used sqlalchemy or_  function make conjunction of expression which allows to execute different expertions using or
# and show the otput on search_result.html
@admin.route("/search/", methods=['POST'])
@admin_required
def search():
    form = SearchForm()
    if form.validate_on_submit():
        value = form.value.data
        doctors = Doctor.query.join(Doctor.specialization).filter(
            or_(
                Doctor.id.ilike(f"%{value}%"),
                Doctor.fname.ilike(f"%{value}%"),
                Doctor.lname.ilike(f"%{value}%"),
                Doctor.email.ilike(f"%{value}%"),
                Doctor.phone.ilike(f"%{value}%"),
                Department.name.ilike(f"%{value}%"),
            )
        ).all()
        patients = Patient.query.filter(
            or_(
                Patient.id.ilike(f"%{value}%"),
                Patient.fname.ilike(f"%{value}%"),
                Patient.lname.ilike(f"%{value}%"),
                Patient.email.ilike(f"%{value}%"),
                Patient.phone.ilike(f"%{value}%")
            )
        ).all()


        return render_template("admin/search_result.html", title="Search Results", value=value, patients=patients, doctors=doctors)
    return redirect(url_for("admin.dashboard"))


@admin.route("/details/<role>/<int:id>", methods=['GET'])
@admin_required
def details(role, id):
    if role == "patient":
        patient = Patient.query.get_or_404(id)
        appointment_ids = Appointment.query.filter_by(patient_id=patient.id).all()
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
        return render_template("patient_details.html", title="Patient Details", patient=patient, role="admin", details=details)
    elif role == "doctor":
        doctor = Doctor.query.get_or_404(id)
        return render_template("doctor_details.html", title="Doctor Details", doctor=doctor, role="admin")
    else:
        flash("Invalid role specified.", "danger")
        return redirect(url_for("admin.dashboard"))



@admin.route('/logout')
@admin_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))
