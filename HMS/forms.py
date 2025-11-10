from flask_wtf import FlaskForm
from wtforms import StringField,SelectField, RadioField, SubmitField, IntegerField, BooleanField, PasswordField, TextAreaField,HiddenField,FormField, FieldList
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from .models import Patient, Doctor



class RegistrationForm(FlaskForm):
    fname = StringField(
        'First name ',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    lname = StringField(
        'Last name',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    age = IntegerField(
        'Age',
        validators=[DataRequired()],
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."),
        Regexp(
            r'^[6-9]\d{9}$',
            message="Please enter a valid 10-digit Indian mobile number."
        )
    ])
    gender = RadioField(
        'Gender',
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        validators=[DataRequired(message="Please select a gender.")]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    confirm_password = PasswordField(
        'Confirm Password', # Label fixed
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = Patient.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose a different one.')


class LoginForm(FlaskForm):
    role = SelectField(
        'Login as',
        choices=[('patient', 'Patient'), ('doctor', 'Doctor')],
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AdminLoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterDoctorForm(FlaskForm):
    fname = StringField(
        'First name ',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    lname = StringField(
        'Last name',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."),
        Regexp(
            r'^[6-9]\d{9}$',
            message="Please enter a valid 10-digit Indian mobile number."
        )
    ])
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    experience = StringField(
        'Experience', validators=[DataRequired(), Length(min=5, max=50)]
    )
    specialization_id = StringField(
        'Specialization ID', validators=[DataRequired()]
    )
    description = StringField(
        'Description', validators=[Length(max=500)]
    )
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = Doctor.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose a different one.')


class PatientProfileEditForm(FlaskForm):
    fname = StringField(
        'First name ',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    lname = StringField(
        'Last name',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."),
        Regexp(
            r'^[6-9]\d{9}$',
            message="Please enter a valid 10-digit Indian mobile number."
        )
    ])
    age = IntegerField(
        'Age',
        validators=[DataRequired()],
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    gender = RadioField(
        'Gender',
        choices=[('male', "Male"), ('female', "Female"), ('other', "Other")],
    )
    submit = SubmitField('Update Profile')

    from .models import Patient

    def __init__(self, patient_to_update, *args, **kwargs):
        super(PatientProfileEditForm, self).__init__(*args, **kwargs)
        self.patient = patient_to_update

    def validate_email(self, email):
        user = Patient.query.filter(
            Patient.email == email.data, 
            Patient.id != self.patient.id  
        ).first()
        
        if user:
            raise ValidationError('Email is already in use by another patient.')

    def validate_phone(self, phone):
        user = Patient.query.filter(
            Patient.phone == phone.data, 
            Patient.id != self.patient.id  
        ).first()

        if user:
            raise ValidationError('Phone number is already in use by another patient.')


class DoctorProfileEditForm(FlaskForm):
    fname = StringField(
        'First name ',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    lname = StringField(
        'Last name',
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )
    phone = StringField('Phone Number', validators=[
        DataRequired(message="Phone number is required."),
        Regexp(
            r'^[6-9]\d{9}$',
            message="Please enter a valid 10-digit Indian mobile number."
        )
    ])
    experience = StringField(
        'Experience', validators=[DataRequired(), Length(min=5, max=50)]
    )
    specialization_id = StringField(
        'Specialization ID', validators=[DataRequired()]
    )
    description = StringField(
        'Description', validators=[Length(max=500)]
    )
    submit = SubmitField('Update Profile')

    def __init__(self, doctor_to_update, *args, **kwargs):
        super(DoctorProfileEditForm, self).__init__(*args, **kwargs)
        self.doctor = doctor_to_update

    def validate_email(self, email):
        user = Doctor.query.filter(
            Doctor.email == email.data, 
            Doctor.id != self.doctor.id 
        ).first()
        
        if user:
            raise ValidationError('Email is already in use by another doctor.')

    def validate_phone(self, phone):
        user = Doctor.query.filter(
            Doctor.phone == phone.data, 
            Doctor.id != self.doctor.id 
        ).first()

        if user:
            raise ValidationError('Phone number is already in use by another doctor.')
        
class SearchForm(FlaskForm):
    value = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')


class UpdateAppointmentForm(FlaskForm):
    visit_type = StringField('Visit Type', validators=[DataRequired()])
    test_done = StringField('Test Done', validators=[DataRequired()])
    diagnosis = TextAreaField('Diagnosis', validators=[DataRequired()])
    medicines = TextAreaField('Medicines', validators=[DataRequired()])
    prescription = TextAreaField('Prescription', validators=[DataRequired()])

    submit = SubmitField('Done')

class AvailabilityDayForm(FlaskForm):
    date_display = StringField('Date')
    
    morning_slot = BooleanField('08:00 - 12:00 am', default=True)
    evening_slot = BooleanField('04:00 - 9:00 pm', default=True)

    class Meta:
        csrf = False

class AvailabilityForm(FlaskForm):
    days = FieldList(
        FormField(AvailabilityDayForm), 
        min_entries=7, 
        max_entries=7
    )
    submit = SubmitField('Save')

class BookAppointmentForm(FlaskForm):
    slot = RadioField(
        'Select an available slot', 
        validators=[DataRequired(message="Please select a time slot.")]
    )
    submit = SubmitField('Book Appointment')
    

