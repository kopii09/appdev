from flask_mysql_connector import MySQL
from cloudinary.uploader import upload
from SSIS_Web.course.course_model import CourseManager




class StudentManager:
    def __init__(self, mysql):
        self.mysql = mysql

    @classmethod
    def init_db(cls, mysql):
        cls.mysql = mysql


    @classmethod
    def search_students_paginated(cls, field, query, page, per_page):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            query_lower = query.lower().strip()
            offset = (page - 1) * per_page
            like_query = f"%{query_lower}%"

            base_sql = """
                SELECT student_info.*, course.code AS course, college.code AS college
                FROM student_info
                LEFT JOIN course ON course.code = student_info.course
                LEFT JOIN college ON college.code = course.college
            """

            allowed_fields = {'id', 'firstname', 'lastname', 'course', 'college', 'year', 'gender'}

            if field == 'all':
                sql = base_sql + """
                    WHERE LOWER(student_info.id) LIKE %s
                    OR LOWER(student_info.firstname) LIKE %s
                    OR LOWER(student_info.lastname) LIKE %s
                    OR LOWER(course.code) LIKE %s
                    OR LOWER(college.code) LIKE %s
                    OR student_info.year = %s
                    OR LOWER(student_info.gender) LIKE %s
                    LIMIT %s OFFSET %s
                """
                params = [like_query, like_query, like_query, like_query, like_query, query, like_query, per_page, offset]


            else:
                if field not in allowed_fields:
                    field = 'id'

                if field == 'course':
                    sql = base_sql + """
                        WHERE (LOWER(course.code) LIKE %s OR course.code IS NULL)
                        LIMIT %s OFFSET %s
                    """
                    params = [like_query, per_page, offset]

                elif field == 'college':
                    sql = base_sql + """
                        WHERE LOWER(college.code) LIKE %s
                        LIMIT %s OFFSET %s
                    """
                else:
                    sql = base_sql + f"""
                        WHERE LOWER(student_info.{field}) LIKE %s
                        LIMIT %s OFFSET %s
                    """
                params = [like_query, per_page, offset]

            print("Executing SQL:", sql)
            print("With params:", params)

            cur.execute(sql, params)
            results = cur.fetchall()
            cur.close()
            return results

        except Exception as e:
            print(f"Error in search_students_paginated: {e}")
            return []





    @classmethod
    def count_students_search(cls, field, query):
        try:
            cur = cls.mysql.connection.cursor()
            query = query.lower().strip()
            like_query = f"%{query}%"

            base_sql = """
                SELECT COUNT(*) FROM student_info
                INNER JOIN course ON course.code = student_info.course
                LEFT JOIN college ON college.code = student_info.college
            """


            if field == 'all':
                sql = base_sql + """
                    WHERE LOWER(student_info.id) LIKE %s
                    OR LOWER(student_info.firstname) LIKE %s
                    OR LOWER(student_info.lastname) LIKE %s
                    OR LOWER(course.name) LIKE %s
                    OR LOWER(student_info.year) LIKE %s
                    OR LOWER(student_info.gender) LIKE %s
                """
                params = [like_query] * 6
            else:
                allowed_fields = {'id', 'firstname', 'lastname', 'course', 'year', 'gender'}
                if field not in allowed_fields:
                    field = 'id'
                
                if field == 'course':
                    sql = base_sql + """
                        WHERE LOWER(course.name) LIKE %s
                    """
                else:
                    sql = base_sql + f"""
                        WHERE LOWER(student_info.{field}) LIKE %s
                    """
                params = [like_query]

            cur.execute(sql, params)
            count = cur.fetchone()[0]
            cur.close()
            return count
        except Exception as e:
            print(f"Error in count_students_search: {e}")
            return 0

    @classmethod
    def get_student_data(cls):
        cur = cls.mysql.connection.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM student_info LEFT JOIN course on course.code = student_info.course")

        student_data = cur.fetchall()
        cur.close()
        return student_data

    @classmethod
    def get_courses(cls):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT code, name FROM course")
            courses = cur.fetchall()
            cur.close()
            return courses
        except Exception as e:
            print(f"Error fetching course: {e}")
            return []

    
    @classmethod
    def add_student(cls, pic_url, studentID, firstname, lastname, course, gender, year, college):
        try:
            conn = cls.mysql.connection
            cursor = conn.cursor()

            query = """
                INSERT INTO student_info (id, firstname, lastname, course, gender, year, pic, college)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (studentID, firstname, lastname, course, gender, year, pic_url, college)

            cursor.execute(query, values)
            conn.commit()
            cursor.close()

            return {'status': 'success', 'message': 'Student added successfully.'}

        except Exception as e:
            print(f"Error adding student: {e}")
            return {'status': 'error', 'message': f'Failed to add student: {e}'}



    @classmethod
    def get_college_by_course(cls, course_name):
        try:
            conn = cls.mysql.connection
            cursor = conn.cursor(dictionary=True)

            query = "SELECT college FROM courses WHERE course = %s LIMIT 1"
            cursor.execute(query, (course_name,))
            result = cursor.fetchone()

            cursor.close()

            return result['college'] if result else None
        except Exception as e:
            print(f"Error fetching college by course: {e}")
            return None



    @classmethod
    def is_duplicate(cls, student_id, exclude_id=None):
        try:
            cur = cls.mysql.connection.cursor()
            if exclude_id:
                # Check if student_id exists and is not the excluded one
                query = "SELECT 1 FROM student_info WHERE id = %s AND id != %s LIMIT 1"
                cur.execute(query, (student_id, exclude_id))
            else:
                # Check if student_id exists at all
                query = "SELECT 1 FROM student_info WHERE id = %s LIMIT 1"
                cur.execute(query, (student_id,))

            exists = cur.fetchone() is not None
            cur.close()
            return exists
        except Exception as e:
            print(f"Error checking duplicate student: {e}")
            return False  # or True, depending on whether you want to be conservative



    @classmethod
    def delete_student(cls, student_id):
        try:
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM student_info WHERE `id` = %s", (student_id,))
            student = cur.fetchone()
            if student:
                cur.execute("DELETE FROM student_info WHERE `id` = %s", (student_id,))
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

            if field and field != 'all':
                cur.execute(
                    f"SELECT * FROM student_info WHERE `{field}` LIKE %s", (f"%{query}%",)
                )
            elif field == 'all':
                cur.execute("""
                    SELECT * FROM student_info 
                    WHERE id LIKE %s OR firstname LIKE %s OR lastname LIKE %s 
                    OR course LIKE %s OR year LIKE %s OR gender LIKE %s
                """, (f"%{query}%",) * 6)
            else:
                flash("Invalid search field.", "danger")
                return []

            student_data = cur.fetchall()
            cur.close()

            if not student_data:
                flash("Student does not exist.", "danger")

            return student_data

        except Exception as e:
            print(f"Error searching students: {e}")
            flash("An error occurred while searching for students.", "danger")
            return []



    @classmethod
    def update_student(cls, pic, firstname, lastname, course, gender, year, id):
        try:
            cur = cls.mysql.connection.cursor()

            if isinstance(pic, str):
                pic_url = pic
            elif pic and getattr(pic, 'filename', '') != '':
                upload_result = upload(pic, folder="SSIS Web", resource_type='image', invalidate=True)
                pic_url = upload_result['secure_url']
            else:
                cur.execute("SELECT pic FROM student_info WHERE `id` = %s", (id,))
                result = cur.fetchone()
                pic_url = result[0] if result else None

            cur.execute("""
                UPDATE student_info SET
                    pic = %s,
                    firstname = %s,
                    lastname = %s,
                    course = %s,
                    gender = %s,
                    year = %s
                WHERE id = %s
            """, (pic_url, firstname, lastname, course, gender, year, id))

            cls.mysql.connection.commit()
            print(f"Updated student {id} picture URL: {pic_url}")
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False



    @classmethod
    def get_student_by_id(cls, student_id):
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

    @classmethod
    def get_student_data_paginated(cls, page, per_page):
        offset = (page - 1) * per_page
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM student_info
                LEFT JOIN course ON course.code = student_info.course
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
