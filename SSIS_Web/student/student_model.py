from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
import os
from flask import current_app as app



class StudentManager:
    def __init__(self, mysql):
        self.mysql = mysql

    @classmethod
    def init_db(cls, mysql):
        cls.mysql = mysql

    @classmethod
    def get_student_data(cls):
        cur = cls.mysql.connection.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM student_info INNER JOIN course on course.code = student_info.course")
        student_data = cur.fetchall()
        cur.close()

        return student_data

    @classmethod
    def get_courses(cls):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT code, name FROM course")
            courses = cur.fetchall()
            # print(courses)
            cur.close()
            return courses
        except Exception as e:
            print(f"Error fetching course: {e}")
            return []

   
    @classmethod
    def add_student(cls, pic, id, firstname, lastname, course, gender, year):
        try:
            cur = cls.mysql.connection.cursor()

            # Check duplicate
            cur.execute("SELECT * FROM student_info WHERE `id` = %s", (id,))
            if cur.fetchone():
                return {'status': 'error', 'message': f"Student with ID '{id}' already exists."}

            # Handle optional picture
            filename = None
            if pic and pic.filename:
                filename = secure_filename(pic.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                pic.save(upload_path)

            # Insert into DB
            cur.execute(
                "INSERT INTO student_info (`pic`, `id`, `firstname`, `lastname`, `course`, `gender`, `year`) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (filename, id, firstname, lastname, course, gender, year)
            )
            cls.mysql.connection.commit()
            return {'status': 'success', 'message': f"Student '{firstname} {lastname}' added successfully."}
        except Exception as e:
            return {'status': 'error', 'message': f"Error adding student: {e}"}



    @classmethod
    def is_duplicate(cls, studentID):
        try:
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM student_info WHERE `id` = %s", (studentID,))
            exists = cur.fetchone() is not None
            cur.close()
            return exists
        except Exception as e:
            print(f"Error checking duplicate: {e}")
            return False

    @classmethod
    def delete_student(cls, student_id):
        try:
            cur = cls.mysql.connection.cursor()
            cur.execute(
                "SELECT * FROM student_info WHERE `id` = %s", (student_id,))
            student = cur.fetchone()
            if student:
                # Delete the student from the database
                print("Deleting student with ID:", student_id)
                cur.execute(
                    "DELETE FROM student_info WHERE `id` = %s", (student_id,))
                cls.mysql.connection.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f"Error deleting student: {e}")
            return False

    @classmethod
    def search_students(cls, field=None, query=None):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)

            if field != 'all':
                # Search by specific field
                cur.execute(
                    f"SELECT * FROM student_info WHERE `{field}` LIKE %s", (f"%{query}%",))
            else:
                # Search by all columns
                cur.execute("SELECT * FROM student_info WHERE id LIKE %s OR firstname LIKE %s OR lastname LIKE %s OR course LIKE %s OR year LIKE %s OR gender LIKE %s",
                            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"{query}"))

            student_data = cur.fetchall()
            cur.close()
            return student_data

        except Exception as e:
            print(f"Error searching students: {e}")
            return None

    @classmethod
    def update_student(cls, pic, old_id, new_id, firstname, lastname, course, gender, year):
        try:
            cur = cls.mysql.connection.cursor()

            # Check if new_id is already taken by another student
            if new_id != old_id:
                cur.execute("SELECT COUNT(*) FROM student_info WHERE `id` = %s", (new_id,))
                if cur.fetchone()[0] > 0:
                    print(f"Student with ID '{new_id}' already exists.")
                    return {'status': 'error', 'message': f"Student ID '{new_id}' is already in use."}

            # Update the record
            cur.execute("""
                UPDATE student_info 
                SET `pic`=%s, `id`=%s, `firstname`=%s, `lastname`=%s, 
                    `course`=%s, `gender`=%s, `year`=%s 
                WHERE `id`=%s
            """, (pic, new_id, firstname, lastname, course, gender, year, old_id))
            
            cls.mysql.connection.commit()
            return {'status': 'success', 'message': 'Student updated successfully.'}

        except Exception as e:
            print(f"Error updating student: {e}")
            return {'status': 'error', 'message': f"Error updating student: {e}"}


    @classmethod
    def get_student_data_paginated(cls, page, per_page):
        offset = (page - 1) * per_page
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM student_info
                INNER JOIN course ON course.code = student_info.course
                ORDER BY student_info.id DESC
                LIMIT %s OFFSET %s
            """
            cur.execute(query, (per_page, offset))
            result = cur.fetchall()
            cur.close()
            return result
        except Exception as e:
            print(f"Error fetching paginated students: {e}")
            return []

    @classmethod
    def get_student_by_id(cls, student_id):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM student_info 
                LEFT JOIN course ON course.code = student_info.course
                LEFT JOIN college ON college.code = student_info.college
                WHERE student_info.id = %s
            """, (student_id,))
            student = cur.fetchone()
            cur.close()
            return student
        except Exception as e:
            print(f"Error fetching student by id: {e}")
            return None


    @classmethod
    def count_students(cls):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) AS count FROM student_info")
            count = cur.fetchone()['count']
            cur.close()
            return count
        except Exception as e:
            print(f"Error counting students: {e}")
            return 0
        
    
