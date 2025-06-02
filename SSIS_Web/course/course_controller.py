from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from SSIS_Web.course.course_model import CourseManager
from flask_mysql_connector import MySQL
from SSIS_Web.course.forms import CourseForm
from SSIS_Web.extensions import csrf

mysql = MySQL()
CourseManager.init_db(mysql)  
course_bp = Blueprint('course', __name__)


@course_bp.route('/courses', methods=['GET', 'POST'])
def list_courses():
    form = CourseForm()
    page = int(request.args.get('page', 1))
    per_page = 10

    if request.method == 'POST':
        search_field = request.form.get('searchField')  
        search_query = request.form.get('searchInput')  
        course_data = CourseManager.search_courses(field=search_field, query=search_query)
        total_courses = len(course_data)
        total_pages = (total_courses + per_page - 1) // per_page
        course_data = course_data[(page - 1) * per_page : page * per_page]
    else:
        total_courses = CourseManager.count_courses()
        total_pages = (total_courses + per_page - 1) // per_page
        course_data = CourseManager.get_course_data_paginated(page, per_page)

    return render_template(
        'course.html',
        course_data=course_data,
        form=form,
        colleges=CourseManager.get_colleges(),
        page=page,
        total_pages=total_pages
    )


@course_bp.route('/courses/add', methods=['GET', 'POST'])
@csrf.exempt
def add_course():
    form = CourseForm()
    page = 1
    per_page = 10
    total_courses = CourseManager.count_courses()
    total_pages = (total_courses + per_page - 1) // per_page

    if request.method == 'POST':
        code = request.form.get('code', '').upper()
        name = request.form.get('name')
        college = request.form.get('college')

        if not all([code, name, college]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('course.list_courses', page=1))

        result = CourseManager.add_course(code, name, college)

        if result['status'] == 'error':
            flash(result['message'], 'danger')
            return redirect(url_for('course.list_courses', page=1))

        flash(result['message'], 'success')
        return redirect(url_for('course.list_courses', page=1))

    # For GET, just redirect to the list view (or you can show the form page if needed)
    return redirect(url_for('course.list_courses', page=1))


@course_bp.route('/api/courses', methods=['POST'])
@csrf.exempt
def api_add_course():
    try:
        data = request.get_json()
        code = data.get('code').upper()
        name = data.get('name')
        college = data.get('college')

        result = CourseManager.add_course(code, name, college)
        if not result:
            return jsonify({"error": "Error adding course. Possibly duplicate code."}), 400

        return jsonify({"message": f"Course {code} added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@course_bp.route('/courses/delete/<string:code>', methods=['POST'])
def delete_course(code):
    try:
        CourseManager.delete_course(code)
        flash(f'Course {code} deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting course: {e}")
        flash('Error deleting course. Please try again.', 'danger')
    return redirect(url_for('course.list_courses'))

@course_bp.route('/courses/edit/<string:code>', methods=['GET'])
@csrf.exempt
def edit_course(code):
    course = CourseManager.get_course_by_code(code)
    return render_template('course.html', course=course, existing_code=code)  
    
@course_bp.route('/courses/edit/', methods=['POST'])
@csrf.exempt
def edit_course_data():
    form = CourseForm()

    updated_data = {
        'new_code': request.form.get('code').upper(),
        'name': request.form.get('name'),
        'college': request.form.get('college'), 
        'old_code': request.form.get('old_code')
    }

    print("Received update data:", updated_data)  # 👈 Add this line for debugging

    if CourseManager.update_course(**updated_data) == Exception:
        flash('Error saving course, duplicate code. Please try again.', 'danger')
    else:
        flash(f'Course {updated_data["new_code"]} updated successfully!', 'success')
    return redirect(url_for('course.list_courses'))
