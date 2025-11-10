from flask import render_template, flash, request, Blueprint, redirect, url_for
from .models import Patient, Doctor, Admin
from .forms import RegistrationForm, LoginForm
from . import db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required, current_user


auth = Blueprint('auth', __name__)

# Register route is only for patients to register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.__class__.__name__ == 'Patient':
            return redirect(url_for('patient.dashboard')) 
        elif current_user.__class__.__name__ == 'Doctor':
            return redirect(url_for('doctor.dashboard')) 
        return redirect(url_for('auth.login')) 

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        patient = Patient(
            fname=form.fname.data, 
            lname=form.lname.data, 
            age=form.age.data, 
            email=form.email.data, 
            phone=form.phone.data, 
            password=hashed_password, 
            gender=form.gender.data
        )
        
        db.session.add(patient)
        db.session.commit()
        flash('Account has been created, you can now log in!', 'success')
        return redirect(url_for('auth.login')) 

    return render_template("register.html", title='Register', form=form)

# it is  a login route where doctor and patient can login by selecting therre role in dropdowm select
# and then, on there basis of provided role, i have initiated the authentication
@auth.route("/", methods=["POST", "GET"])
def login():

    # checking wheather patient/doctor is already loggedin or session is alive then directing to respective dashboard
    if current_user.is_authenticated:
        if current_user.__class__.__name__ == 'Patient':
            return redirect(url_for('patient.dashboard')) 
        elif current_user.__class__.__name__ == 'Doctor':
            return redirect(url_for('doctor.dashboard', ))
        return redirect(url_for('auth.login')) 

    form = LoginForm()
    if form.validate_on_submit():
        if form.role.data == 'patient':
            patient = Patient.query.filter_by(email=form.email.data).first()
            if patient and bcrypt.check_password_hash(patient.password, form.password.data):
                if patient.blacklisted:
                    flash("Your account has been blacklisted. Please contact support.", "danger")
                    return redirect(url_for("auth.login"))
                login_user(patient, remember=form.remember.data)
                
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("patient.dashboard"))
            else:
                flash("Login Unsuccessful. Please check email and password", "danger")
            
        elif form.role.data == 'doctor':
            doctor = Doctor.query.filter_by(email=form.email.data).first()
            if doctor and bcrypt.check_password_hash(doctor.password, form.password.data):
                if doctor.blacklisted:
                    flash("Your account has been blacklisted. Please contact support.", "danger")
                    return redirect(url_for("auth.login"))
                login_user(doctor, remember=form.remember.data)
                
                next_page = request.args.get("next")
                return redirect(next_page) if next_page else redirect(url_for("doctor.dashboard"))
            else:
                flash("Login Unsuccessful. Please check email and password", "danger")
            
    return render_template("login.html", title='Login', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

