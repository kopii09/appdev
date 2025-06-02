from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from SSIS_Web.student.student_model import StudentManager
from flask_mysql_connector import MySQL
from SSIS_Web.student.forms import StudentForm
from cloudinary import uploader
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from SSIS_Web.extensions import csrf
from SSIS_Web.student.student_model import StudentManager


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

    # Pagination parameters
    page = request.args.get('page', 1, type=int)  # default to page 1
    per_page = 10  # number of students per page, you can adjust

    if request.method == 'POST':
        search_field = request.form.get('searchField')
        search_query = request.form.get('searchInput')
        # Perform search (you can extend pagination here too if needed)
        student_data = StudentManager.search_students(
            field=search_field, query=search_query)
    else:
        # Retrieve paginated students instead of all
        student_data = StudentManager.get_student_data_paginated(page=page, per_page=per_page)

    # You also want to know total count for pagination UI
    total_students = StudentManager.count_students()

    total_pages = (total_students + per_page - 1) // per_page

    return render_template('student.html',
                           student_data=student_data,
                           form=form,
                           courses=courses,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages)



from flask import render_template, request, redirect, url_for, flash

@student_bp.route('/students/add', methods=['GET', 'POST'])
@csrf.exempt
def add_student():
    form = StudentForm()
    page = 1
    per_page = 10
    total_students = StudentManager.count_students()
    total_pages = (total_students + per_page - 1) // per_page

    if request.method == 'POST':
        studentID = request.form.get('studentID')

        if StudentManager.is_duplicate(studentID):
            flash(f"Student with ID {studentID} already exists.", "danger")
            return redirect(url_for('student.list_students'))

        pic = request.files.get('pic')
        id = studentID
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        course = request.form.get('course')
        gender = request.form.get('gender')
        year = request.form.get('year')

        if not all([id, firstname, lastname, course, gender, year]):
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for('student.add_student'))

        result = StudentManager.add_student(pic, id, firstname, lastname, course, gender, year)

        if result['status'] == 'success':
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'danger')

        # Redirect to first page of student list to see the new student
        return redirect(url_for('student.list_students', page=1))

    return render_template(
        'student.html',
        form=form,
        courses=StudentManager.get_courses(),
        student_data=StudentManager.get_student_data_paginated(page, per_page),
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


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
        upload_result = upload(pic, folder="SSIS Web", resource_type='image')
        secure_url = upload_result['secure_url']
    else:
        secure_url = request.form.get('image_url1') or None  # fallback

    new_id = request.form.get('studentID')
    old_id = request.form.get('originalStudentID')  # Make sure form includes this hidden input!

    # Check for duplicate only if new ID ≠ old ID
    if new_id != old_id and StudentManager.is_duplicate(new_id):
        flash(f"A student with ID {new_id} already exists.", "danger")
        return redirect(url_for('student.list_students'))

    updated_data = {
        'pic': secure_url,
        'new_id': new_id,
        'firstname': request.form.get('firstname'),
        'lastname': request.form.get('lastname'),
        'course': request.form.get('course'),
        'year': request.form.get('year'),
        'gender': request.form.get('gender'),
        'old_id': old_id
    }

    try:
        if StudentManager.update_student(**updated_data):
            flash(f'Student {new_id} updated successfully!', 'success')
        else:
            flash('Error saving student. Please try again.', 'danger')
    except Exception as e:
        flash(f'Error: {e}', 'danger')

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

@student_bp.route('/students/edit/<string:student_id>', methods=['GET'])
def show_edit_student_form(student_id):
    student = StudentManager.get_student_by_id(student_id)
    courses = StudentManager.get_courses()

    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('student.list_students'))

    # Pass the student data and courses to the edit form template
    return render_template('student.html', student=student, courses=courses)

