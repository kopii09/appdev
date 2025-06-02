from flask import Blueprint, render_template, request, redirect, url_for, flash
from SSIS_Web.college.college_model import CollegeManager
from flask_mysql_connector import MySQL
from SSIS_Web.college.forms import CollegeForm
from SSIS_Web.extensions import csrf

mysql = MySQL()
CollegeManager.init_db(mysql)
college_bp = Blueprint('college', __name__)

@college_bp.route('/colleges')
def list_colleges():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    total_colleges = CollegeManager.count_colleges()
    total_pages = (total_colleges + per_page - 1) // per_page
    college_data = CollegeManager.get_college_data_paginated(page, per_page)
    form = CollegeForm()
    return render_template('college.html',
                           form=form,
                           college_data=college_data,
                           page=page,
                           total_pages=total_pages,
                           existing_code=None)


@college_bp.route('/colleges/add', methods=['POST'])
@csrf.exempt
def add_college():
    form = CollegeForm()
    if form.validate_on_submit():
        code = form.code.data.upper()
        name = form.name.data

        result = CollegeManager.add_college(code, name)
        if result.get('status') == 'error':
            flash(result.get('message', 'Error adding college.'), 'danger')
            return redirect(url_for('college.list_colleges'))
        else:
            flash(f'College {code} added successfully!', 'success')
            return redirect(url_for('college.list_colleges'))

    # form not valid (optional handling)
    flash('Invalid input. Please check the form.', 'danger')
    return redirect(url_for('college.list_colleges'))


@college_bp.route('/colleges/delete/<string:code>', methods=['POST'])
@csrf.exempt
def delete_college(code):
    try:
        CollegeManager.delete_college(code)
        flash(f'College {code} deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting college: {e}")
        flash('Error deleting college. Please try again.', 'danger')
    return redirect(url_for('college.list_colleges'))


@college_bp.route('/colleges/edit/<string:old_code>', methods=['GET', 'POST'])
def edit_college(old_code):
    form = CollegeForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            new_code = form.code.data.upper()
            name = form.name.data

            result = CollegeManager.update_college(old_code, new_code, name)
            if result.get('status') == 'error':
                flash(result.get('message'), 'danger')
                # Redirect back to edit page so user can fix it
                return redirect(url_for('college.edit_college', old_code=old_code))

            flash(f'College {new_code} updated successfully!', 'success')
            # On success, go back to college list
            return redirect(url_for('college.list_colleges'))
        else:
            # Form validation failed, just render the form with errors
            flash('Please correct the errors in the form.', 'danger')

    # GET or form errors — load existing college data to fill form
    college = CollegeManager.get_college_by_code(old_code)
    if not college:
        flash('College not found.', 'warning')
        return redirect(url_for('college.list_colleges'))

    # Pre-fill form fields with existing college info
    form.code.data = college['code']
    form.name.data = college['name']

    # Optionally load paginated college list or other data here if needed
    # college_data = CollegeManager.get_college_data_paginated(page=1, per_page=10)

    return render_template('edit_college.html', form=form, old_code=old_code)


@college_bp.route('/colleges/edit/', methods=['POST'])
@csrf.exempt
def edit_college_data():
    form = CollegeForm()
    updated_code = form.code.data.upper()
    updated_name = form.name.data
    old_code = request.form.get('old_code')
    page = int(request.form.get('page', 1))  # <-- important fix

    if form.validate_on_submit():
        updated_data = {
            'new_code': updated_code,
            'name': updated_name,
            'old_code': old_code
        }
        try:
            result = CollegeManager.update_college(**updated_data)
            if result.get('status') == 'error':
                flash(result.get('message', 'Error updating college. Possibly duplicate code or name.'), 'danger')

                # Repopulate the list with correct page
                per_page = 10
                total_colleges = CollegeManager.count_colleges()
                total_pages = (total_colleges + per_page - 1) // per_page or 1
                college_data = CollegeManager.get_college_data_paginated(page, per_page)

                # Refill the form
                form.code.data = updated_code
                form.name.data = updated_name

                return render_template(
                    'college.html',
                    college_data=college_data,
                    form=form,
                    existing_code=old_code,
                    page=page,
                    total_pages=total_pages
                )

            flash(f'College {updated_code} updated successfully!', 'success')
        except Exception as e:
            print(f"Error updating college: {e}")
            flash('Error updating college. Please try again.', 'danger')
            return redirect(url_for('college.edit_college', code=old_code))
    else:
        flash('Invalid form data. Please correct and try again.', 'danger')
        return redirect(url_for('college.edit_college', code=old_code))

    return redirect(url_for('college.list_colleges'))
