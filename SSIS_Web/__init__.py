from flask import Flask
from config import DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HOST, SECRET_KEY, CLOUD_NAME, CLOUD_APIKEY, CLOUDINARY_SECRET
import cloudinary

from SSIS_Web.extensions import csrf, mysql, bootstrap  

from SSIS_Web.student.student_model import StudentManager


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_url_path='/static')
    
    app.config.from_mapping(
        SECRET_KEY=SECRET_KEY,
        MYSQL_USER=DB_USERNAME,
        MYSQL_PASSWORD=DB_PASSWORD,
        MYSQL_DATABASE=DB_NAME,
        MYSQL_HOST=DB_HOST,
    )

    cloudinary.config(
        cloud_name= "dkxbgqdjl",
        api_key= "568291822549319",
        api_secret= "tkwLUcIojJPXEk75jom4HCovsIo",
        secure=True
    )

    # Initialize extensions
    csrf.init_app(app)
    mysql.init_app(app)
    bootstrap.init_app(app)

    # Initialize your manager
    student_manager = StudentManager(mysql)

    # Register blueprints
    from .student.student_controller import student_bp as student_blueprint
    app.register_blueprint(student_blueprint)

    from .course.course_controller import course_bp as course_blueprint
    app.register_blueprint(course_blueprint)

    from .college.college_controller import college_bp as college_blueprint
    app.register_blueprint(college_blueprint)

    return app
