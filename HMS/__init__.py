from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate 

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, template_folder ='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./hmsdb.db'

    db.init_app(app)

    # import routes
    from .auth import registerd_routes
    registerd_routes(app, db)

    migrate = Migrate(app, db)

    return app