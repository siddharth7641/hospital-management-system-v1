from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
DB_NAME = "hmsdb.db"

# i have imported the models here to avoid circular import issues
from .models import Patient , Doctor, Admin

@login_manager.user_loader
def load_user(string_user_id):
    if not string_user_id or '-' not in string_user_id:
        return None
        
    try:
        user_type, user_id = string_user_id.split('-')
        user_id = int(user_id)
    except ValueError:
        return None 

    if user_type == 'admin':
        return Admin.query.get(user_id)
    elif user_type == 'patient':
        return Patient.query.get(user_id)
    elif user_type == 'doctor':
        return Doctor.query.get(user_id)

    return None


login_manager.login_view = 'auth.login'
login_manager.login_message_category = "info"

def create_app():
    
    app = Flask(__name__, template_folder ='templates') 
    app.config['SECRET_KEY'] = '43e823a1b2eebb7b1c9c104a54b2b52e0fe8e04c'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///./{DB_NAME}'

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .auth import auth  
    from .admin import admin 
    from .patient import patient
    from .doctor import doctor
    
    app.register_blueprint(auth )
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(patient, url_prefix='/patient')
    app.register_blueprint(doctor, url_prefix='/doctor')

    login_manager.blueprint_login_views = {
        'admin': 'admin.login',
        'patient': 'auth.login',
        'doctor': 'auth.login'
    }
    create_database(app)

    return app


def create_database(app):
    # This check if the database file already exists in the 'HMS' folder
    if not path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
            print("Database created successfully.")
            
            admin = Admin.query.filter_by(username="Sid").first()
            if not admin:
                hashed_password = bcrypt.generate_password_hash("sid123").decode('utf-8')
                new_admin = Admin(username = "Sid",  
                                  password = hashed_password,
                                  fname="Siddharth", 
                                  lname='tiwari' ,
                                  email = "sid@gmail.com")
                
                db.session.add(new_admin)
                db.session.commit()
                print("SuperUser admin 'Sid' created.")