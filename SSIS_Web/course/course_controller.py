from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from SSIS_Web.course.course_model import CourseManager
from flask_mysql_connector import MySQL
from SSIS_Web.course.forms import CourseForm

mysql = MySQL()
CourseManager.init_db(mysql)  
course_bp = Blueprint('course', __name__)


@course_bp.route('/courses', methods=['GET', 'POST'])
def list_courses():
    form = CourseForm()
    colleges = CourseManager.get_colleges()
    
    if request.method == 'POST':
        search_field = request.form.get('searchField')  
        search_query = request.form.get('searchInput')  
        # Perform search based on user input
        course_data = CourseManager.search_courses(field=search_field, query=search_query)
    else:
        # If no search input, retrieve all courses
        course_data = CourseManager.get_course_data()

    return render_template('course.html', course_data=course_data, form=form, colleges=colleges)

@course_bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    form = CourseForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Get data from the form submission
        code = request.form.get('code').upper()
        name = request.form.get('name')
        college = request.form.get('college')
        
        if CourseManager.add_course(code, name, college) == Exception:
            flash('Error adding course. Please try again.', 'error')
        else:
            flash(f'Course {code} added successfully!', 'success')
        return redirect(url_for('course.list_courses'))
        #except Exception as e:
         #   print(f"Error adding course: {e}")
          #  flash('Error adding course. Please try again.', 'error')
    return render_template('course.html', form=form)

@course_bp.route('/courses/delete/<string:code>', methods=['POST'])
def delete_course(code):
    try:
        CourseManager.delete_course(code)
        flash(f'Course {code} deleted successfully!', 'success')
        return redirect(url_for('course.list_courses'))
    except Exception as e:
        print(f"Error deleting course: {e}")
        flash('Error deleting course. Please try again.', 'error')
        
@course_bp.route('/courses/edit/<string:code>', methods=['GET'])
def edit_course(code):
    course = CourseManager.get_course_by_code(code)
    return render_template('course.html', course=course, existing_code=code)  
    
@course_bp.route('/courses/edit/', methods=['POST'])
def edit_course_data():
    form = CourseForm() 
    #form_data = request.form
    #print("Form Data received:", form_data)
    updated_data = {
        'new_code': request.form.get('code').upper(),
        'name': request.form.get('name'),
        'college': request.form.get('college'), 
        'old_code': request.form.get('old_code')
    }
    if CourseManager.update_course( **updated_data) == Exception:
        flash('Error saving course, duplicate code. Please try again.', 'error')
    else:
        flash(f'Course {updated_data["new_code"]} updated successfully!', 'success')
    return redirect(url_for('course.list_courses'))
