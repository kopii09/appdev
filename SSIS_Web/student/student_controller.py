from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from SSIS_Web.student.student_model import StudentManager
from flask_mysql_connector import MySQL
from SSIS_Web.student.forms import StudentForm
from cloudinary import uploader
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from SSIS_Web.extensions import csrf
from SSIS_Web.student.student_model import StudentManager
from SSIS_Web.course.course_model import CourseManager




mysql = MySQL()
student_bp = Blueprint('student', __name__)
StudentManager.init_db(mysql)


@student_bp.route('/')
def home():
    return render_template('home.html')


@student_bp.route('/students', methods=['GET'])
def list_students():
    form = StudentForm()
    courses = StudentManager.get_courses()

    page = request.args.get('page', 1, type=int)
    per_page = 10

    search_field = request.args.get('searchField', 'all')
    search_query = request.args.get('searchInput', '').strip()

    if search_query:
        student_data = StudentManager.search_students_paginated(
            field=search_field, query=search_query, page=page, per_page=per_page)
        total_students = StudentManager.count_students_search(field=search_field, query=search_query)
    else:
        student_data = StudentManager.get_student_data_paginated(page=page, per_page=per_page)
        total_students = StudentManager.count_students()

    total_pages = (total_students + per_page - 1) // per_page

    return render_template('student.html',
                           student_data=student_data,
                           form=form,
                           courses=courses,
                           page=page,
                           per_page=per_page,
                           total_pages=total_pages,
                           search_field=search_field,
                           search_query=search_query)



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
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        course_code = request.form.get('course')
        gender = request.form.get('gender')
        year = request.form.get('year')
        pic = request.files.get('pic')

        # Validate required fields
        if not all([studentID, firstname, lastname, course_code, gender, year]):
            flash("Please fill in all required fields.", "danger")
            return render_template(
                'student.html',
                form=form,
                courses=StudentManager.get_courses(),
                student_data=StudentManager.get_student_data_paginated(page, per_page),
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                duplicate_error=True,
                duplicate_message="Please fill in all required fields.",
                form_data=request.form
            )

        # Check duplicate student ID
        if StudentManager.is_duplicate(studentID):
            flash(f"Student with ID {studentID} already exists.", "danger")
            return render_template(
                'student.html',
                form=form,
                courses=StudentManager.get_courses(),
                student_data=StudentManager.get_student_data_paginated(page, per_page),
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                duplicate_error=True,
                duplicate_message=f"Student with ID {studentID} already exists.",
                form_data=request.form
            )

        # Upload image to Cloudinary if pic uploaded
        pic_url = None
        if pic and pic.filename != '':
            try:
                upload_result = upload(pic, folder="SSIS Web", resource_type='image')
                pic_url = upload_result.get('secure_url')
            except Exception as e:
                flash(f"Error uploading image: {e}", "danger")
                pic_url = None

        # Fetch course details to get college
        course_record = CourseManager.get_course_by_code(course_code)
        if course_record:
            college = course_record.get('college')
        else:
            college = None  # or handle the error if needed

        # Add student to DB including college
        result = StudentManager.add_student(pic_url, studentID, firstname, lastname, course_code, gender, year, college)

        if result['status'] == 'success':
            flash(result['message'], 'success')
            return redirect(url_for('student.list_students', page=1))
        else:
            flash(result['message'], 'danger')
            return render_template(
                'student.html',
                form=form,
                courses=StudentManager.get_courses(),
                student_data=StudentManager.get_student_data_paginated(page, per_page),
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                duplicate_error=True,
                duplicate_message=result['message'],
                form_data=request.form
            )

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

    # Get uploaded picture and existing picture URL
    pic = request.files.get('pic1')  # New uploaded file
    existing_pic_url = request.form.get('image_url1')  # Existing Cloudinary image URL

    # ✅ Get the student ID from the hidden field in the form
    student_id = request.form.get('originalStudentID')  # <--- Make sure this is present in the form

    # Upload new image if available
    if pic and pic.filename != '':
        upload_result = upload(pic, folder="SSIS Web", resource_type='image')
        new_pic_url = upload_result['secure_url']
    else:
        new_pic_url = existing_pic_url or None

    updated_data = {
        'pic': new_pic_url,
        'firstname': request.form.get('firstname'),
        'lastname': request.form.get('lastname'),
        'course': request.form.get('course'),
        'year': request.form.get('year'),
        'gender': request.form.get('gender'),
        'id': student_id  # ✅ Must not be blank
    }

    print("Updating with data:", updated_data)

    try:
        if StudentManager.update_student(**updated_data):
            flash(f'Student {student_id} updated successfully!', 'success')
        else:
            flash('Error saving student. Please try again.', 'danger')
    except Exception as e:
        flash(f'Error: {e}', 'danger')

    return redirect(url_for('student.list_students'))




@student_bp.route('/students/<string:student_id>/photo', methods=['POST'])
def update_student_photo(student_id):
    pic = request.files.get('photo')
    if not pic or pic.filename == '':
        return jsonify({"error": "No image uploaded"}), 400

    try:
        upload_result = upload(pic, folder="SSIS Web", resource_type='image')
        secure_url = upload_result['secure_url']

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

