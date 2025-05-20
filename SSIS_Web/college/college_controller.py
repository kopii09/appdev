from flask import Blueprint, render_template, request, redirect, url_for, flash
from SSIS_Web.college.college_model import CollegeManager
from flask_mysql_connector import MySQL
from SSIS_Web.college.forms import CollegeForm

mysql = MySQL()
CollegeManager.init_db(mysql)  
college_bp = Blueprint('college', __name__)

@college_bp.route('/colleges', methods=['GET', 'POST'])
def list_colleges():
    form = CollegeForm()
    
    if request.method == 'POST':
        search_field = request.form.get('searchField')  
        search_query = request.form.get('searchInput')  
        # Perform search based on user input
        college_data = CollegeManager.search_colleges(field=search_field, query=search_query)
    else:
        # If no search input, retrieve all colleges
        college_data = CollegeManager.get_college_data()
        
    return render_template('college.html', college_data=college_data, form=form)


@college_bp.route('/colleges/add', methods=['GET', 'POST'])
def add_college():
    form = CollegeForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Get data from the form submission
        code = request.form.get('code').upper()
        name = request.form.get('name')
        try:
            CollegeManager.add_college(code, name)
            flash(f'College {code} added successfully!', 'success')
            return redirect(url_for('college.list_colleges'))
        except Exception as e:
            print(f"Error adding college: {e}")
            flash('Error deleting college. Please try again.', 'error')
    return render_template('college.html', form=form)


@college_bp.route('/colleges/delete/<string:code>', methods=['POST'])
def delete_college(code):
    try:
        CollegeManager.delete_college(code)
        flash(f'College {code} added successfully!', 'success')
        return redirect(url_for('college.list_colleges'))
    except Exception as e:
        print(f"Error deleting college: {e}")
        flash('Error deleting college. Please try again.', 'error')
        
@college_bp.route('/colleges/edit/<string:code>', methods=['GET'])
def edit_college(code):
    college = CollegeManager.get_college_by_code(code)
    return render_template('college.html', college=college, existing_code=code)  

@college_bp.route('/colleges/edit/', methods=['POST'])
def edit_college_data():
    form = CollegeForm() 
    updated_data = {
        'new_code': request.form.get('code').upper(),
        'name': request.form.get('name'), 
        'old_code': request.form.get('old_code')
    }
    CollegeManager.update_college( **updated_data)
    flash(f'College {updated_data["new_code"]} updated successfully!', 'success') 
    return redirect(url_for('college.list_colleges'))
