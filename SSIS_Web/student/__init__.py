from flask import Blueprint

student_bp = Blueprint('student', __name__)



from SSIS_Web.student import student_controller