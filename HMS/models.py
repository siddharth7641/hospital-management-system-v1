from . import db


# login stuff brainstorm 

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Admin {self.username}>"

class Doctor(db.Model):
    __tablename__ ='doctor'
    id = db.Column(db.Integer , primary_key =True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable= False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100),unique=True,nullable =False)
    phone = db.Column(db.String(10), nullable =False)
    experience = db.Column(db.Text, nullable = False)
    description = db.Column(db.Text )
    specialization_id = db.Column(db.Integer,db.ForeignKey('department.id'), nullable= False) #link
    
    availability = db.relationship('Availability', backref ='doctor', lazy=True)
    appointments= db.relationship('Appointment', backref= 'doctor', lazy=True)

    def __repr__(self):
        return f"<Doctor {self.name} - {self.department.name}>"


class Patient(db.Model) :
    __tablename__ = 'patient'
    id = db.Column(db.Integer , primary_key =True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=True)
    age = db.Column(db.Integer , nullable= False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(100), nullable =False)
    phone = db.Column(db.String(10), nullable =False)

    appointments =db.relationship('Appointment', backref ='patient', lazy=True)

    def __repr__(self):
        return f"<Patient {self.name}>"


class Appointment(db.Model):
    __tablename__ ='appointment'
    id = db.Column(db.Integer , primary_key =True)
    doctor_id= db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable= False) #link
    patient_id = db.Column(db.Integer,db.ForeignKey('patient.id'), nullable =False ) #link
    status = db.Column(db.String(20), default ="Booked")
    time = db.Column(db.Time, nullable =False)
    date = db.Column(db.Date, nullable =False)

    treatment = db.relationship('Treatment', backref='appointment', uselist = False)

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', 'time', name='unique_doctor_appointment'),
    )

    
class Treatment(db.Model):
    __tablename__ ='treatment'
    id = db.Column(db.Integer , primary_key =True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'),nullable= False )
    diagnosis = db.Column(db.Text, nullable = False)
    tests_done = db.Column(db.Text, ) 
    visit_type =  db.Column(db.String(50), nullable= False) # brainstorm
    prescription = db.Column(db.Text)
    medicines = db.Column(db.Text)



class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(40), nullable = False)
    description = db.Column(db.Text, nullable = False)

    doctors_registered = db.relationship('Doctor', backref='department' , lazy= True)

    def __repr__(self):
        return f"<Department {self.name}>"


class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    morning_slot = db.Column(db.String(50))   
    evening_slot = db.Column(db.String(50))   
    is_available = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', name='unique_doctor_date'),
    )



