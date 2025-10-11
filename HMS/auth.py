from flask import render_template , request, Blueprint
from .models import *

auth_bp = Blueprint('auth', __name__)

def registerd_routes(app , db):
    @app.route('/')
    def index():
        doctors = Doctor.query.all()
        return render_template('login.html', doctors = doctors)