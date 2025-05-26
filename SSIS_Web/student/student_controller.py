from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from SSIS_Web.student.student_model import StudentManager
from flask_mysql_connector import MySQL
from SSIS_Web.student.forms import StudentForm
from cloudinary import uploader
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from SSIS_Web.extensions import csrf

mysql = MySQL()
student_bp = Blueprint('student', __name__)
StudentManager.init_db(mysql)


@student_bp.route('/')
def home():
    return render_template('home.html')


@student_bp.route('/students', methods=['GET', 'POST'])
def list_students():
    form = StudentForm()
    courses = StudentManager.get_courses()

    if request.method == 'POST':
        search_field = request.form.get('searchField')
        search_query = request.form.get('searchInput')
        # Perform search based on user input
        student_data = StudentManager.search_students(
            field=search_field, query=search_query)
    else:
        # If no search input, retrieve all students
        student_data = StudentManager.get_student_data()

    return render_template('student.html', student_data=student_data, form=form, courses=courses)


@student_bp.route('/students/add', methods=['GET', 'POST'])
@csrf.exempt
def add_student():
    form = StudentForm()

    if request.method == 'POST':
        if request.content_type.startswith('multipart/form-data'):
            # Handle form submission (from browser or Postman)
            student_pic = request.files.get('pic')
            student_id = request.form.get('studentID')
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            course_code = request.form.get('course')
            year = request.form.get('year')
            gender = request.form.get('gender')

            if student_pic:
                upload_result = upload(student_pic, folder="SSIS Web", resource_type='image')
                secure_url = upload_result['secure_url']
            else:
                secure_url = None

            result = StudentManager.add_student(secure_url, student_id, first_name, last_name, course_code, gender, year)
            if result == Exception:
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'error': 'Duplicate ID'}), 400
                flash('Error adding student, duplicate ID.', 'error')
            else:
                if request.headers.get('Accept') == 'application/json':
                    return jsonify({'message': f'Student {student_id} added successfully!'}), 200
                flash(f'Student {student_id} added successfully!', 'success')
            return redirect(url_for('student.list_students'))
        else:
            return jsonify({'error': 'Unsupported Content-Type'}), 400

    return render_template('student.html', form=form)

@student_bp.route('/students/delete/<string:student_id>', methods=['POST'])
@csrf.exempt
def delete_student(student_id):
    try:
        StudentManager.delete_student(student_id)
        flash(f'Student {student_id} deleted successfully!', 'success')
        return redirect(url_for('student.list_students'))
    except Exception as e:
        print(f"Error deleting student: {e}")
        flash('Error deleting student. Please try again.', 'error')


@student_bp.route('/students/edit/', methods=['POST'])
@csrf.exempt
def edit_student_data():
    form = StudentForm()
    pic = request.files.get('pic1')
    if pic:
        upload_result = upload(
            pic, folder="SSIS Web", resource_type='image')
        secure_url = upload_result['secure_url']
    else:
        secure_url = None
    gender = request.form.get('gender')
    print("URL: ", secure_url)

    updated_data = {
        'pic': secure_url,
        'new_id': request.form.get('studentID'),
        'firstname': request.form.get('firstName'),
        'lastname': request.form.get('lastName'),
        'course': request.form.get('course'),
        'year': request.form.get('year'),
        'gender': request.form.get('gender'),
        'old_id': request.form.get('old_id')
    }

    try:
        if StudentManager.update_student(**updated_data):
            flash(
                f'Student {updated_data["new_id"]} updated successfully!', 'success')
        else:
            flash('Error saving student. Please try again.', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
        # Log the exception for debugging purposes
    return redirect(url_for('student.list_students'))

@student_bp.route('/students/<string:student_id>/photo', methods=['POST'])
def update_student_photo(student_id):
    pic = request.files.get('photo')
    if not pic:
        return jsonify({"error": "No image uploaded"}), 400

    try:
        upload_result = upload(pic, folder="SSIS Web", resource_type='image')
        secure_url = upload_result['secure_url']

        # Fetch student to get other values
        student = StudentManager.get_student_by_id(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        StudentManager.update_student(
            pic=secure_url,
            old_id=student_id,
            new_id=student_id,
            firstname=student['firstname'],
            lastname=student['lastname'],
            course=student['course'],
            gender=student['gender'],
            year=student['year']
        )
        return jsonify({"message": "Photo updated", "url": secure_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

