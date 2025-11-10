from . import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id_string):
    """
    Load a user given the 'namespaced' user_id string (e.g., "admin-1").
    so that it could differentiate b/w same id exist in different tables for different roles
    """
    if not user_id_string or '-' not in user_id_string:
        return None
        
    try:
        user_type, user_id = user_id_string.split('-')
        user_id = int(user_id)
    except ValueError:
        return None # Malformed ID

    if user_type == 'admin':
        return Admin.query.get(user_id)
    elif user_type == 'doctor':
        return Doctor.query.get(user_id)
    elif user_type == 'patient':
        return Patient.query.get(user_id)
    
    return None


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"
    
    # defining get id because when isinstance was checking if this curr_user is instance of which table by id, it was finding that same id exist in patien and admin both  and didnot allowed to login and showed 'forbidden'
    # now adding prefix befor returning an id, it will be able to distinguish b/w them
    def get_id(self): return f"admin-{self.id}"


class Doctor(db.Model, UserMixin):
    __tablename__ ='doctor'
    id = db.Column(db.Integer , primary_key =True)
    password = db.Column(db.String(100), nullable= False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100),unique=True,nullable =False)
    phone = db.Column(db.String(10), nullable =False)
    experience = db.Column(db.Text, nullable = False)
    description = db.Column(db.Text )
    specialization_id = db.Column(db.Integer,db.ForeignKey('department.id'), nullable= False) 
    blacklisted = db.Column(db.Boolean, default=False)
    
    specialization = db.relationship('Department', backref='doctors', lazy=True)
    availability = db.relationship('Availability', backref ='doctor', lazy=True,cascade="all, delete-orphan")
    appointments= db.relationship('Appointment', backref= 'doctor', lazy=True, cascade="all, delete-orphan")


    def __repr__(self):
        return f"<Doctor {self.fname} - {self.specialization.name}>"
    
    def get_id(self): return f"doctor-{self.id}"

class Patient(db.Model, UserMixin) :
    __tablename__ = 'patient'
    id = db.Column(db.Integer , primary_key =True)
    password = db.Column(db.String(200), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer , nullable= False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable =False)
    phone = db.Column(db.String(10), nullable =False)
    blacklisted = db.Column(db.Boolean, default=False)

    appointments =db.relationship('Appointment', backref ='patient', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.fname}>"
    
    def get_id(self): return f"patient-{self.id}"


class Appointment(db.Model):
    __tablename__ ='appointment'
    id = db.Column(db.Integer , primary_key =True)
    doctor_id= db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable= False) #link
    patient_id = db.Column(db.Integer,db.ForeignKey('patient.id'), nullable =False ) #link
    status = db.Column(db.String(20), default ="Booked")
    time = db.Column(db.Time, nullable =False)
    date = db.Column(db.Date, nullable =False)

    treatment = db.relationship('Treatment', backref='appointment', uselist = False,cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', 'time', name='unique_doctor_appointment'),
    )

    
class Treatment(db.Model):
    __tablename__ ='treatment'
    id = db.Column(db.Integer , primary_key =True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'),nullable= False )
    diagnosis = db.Column(db.Text, nullable = False)
    tests_done = db.Column(db.Text, ) 
    visit_type =  db.Column(db.String(50), nullable= False) 
    prescription = db.Column(db.Text)
    medicines = db.Column(db.Text)

class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(40), nullable = False)
    description = db.Column(db.Text, nullable = False)


    def __repr__(self):
        return f"<Department {self.name}>"


class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    morning_slot = db.Column(db.Boolean, default=True)   
    evening_slot = db.Column(db.Boolean, default=True)   

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', name='unique_doctor_date'),
    )



