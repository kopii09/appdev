from flask_mysql_connector import MySQL
from cloudinary.uploader import upload



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
            cur.close()
            return courses
        except Exception as e:
            print(f"Error fetching course: {e}")
            return []

    @classmethod
    def add_student(cls, pic, id, firstname, lastname, course, gender, year):
        try:
            cur = cls.mysql.connection.cursor()

            # Check duplicate student ID
            cur.execute("SELECT * FROM student_info WHERE `id` = %s", (id,))
            if cur.fetchone():
                return {'status': 'error', 'message': f"Student with ID '{id}' already exists."}

            pic_url = None
            if pic and pic.filename != '':
                try:
                    print(f"Uploading file: {pic.filename}")
                    upload_result = upload(pic, folder="SSIS Web", resource_type='image')  # or pic.stream if needed
                    pic_url = upload_result['secure_url']
                    print(f"Upload successful: {pic_url}")
                except Exception as e:
                    print(f"Cloudinary upload failed: {e}")
                    return {'status': 'error', 'message': f"Image upload failed: {e}"}
            else:
                print("No image uploaded")

            cur.execute(
                "INSERT INTO student_info (`pic`, `id`, `firstname`, `lastname`, `course`, `gender`, `year`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (pic_url, id, firstname, lastname, course, gender, year)
            )
            cls.mysql.connection.commit()
            return {'status': 'success', 'message': f"Student '{firstname} {lastname}' added successfully."}

        except Exception as e:
            print(f"Exception: {e}")
            return {'status': 'error', 'message': f"Error adding student: {e}"}



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

            if field != 'all':
                cur.execute(
                    f"SELECT * FROM student_info WHERE `{field}` LIKE %s", (f"%{query}%",))
            else:
                cur.execute("""
                    SELECT * FROM student_info 
                    WHERE id LIKE %s OR firstname LIKE %s OR lastname LIKE %s 
                    OR course LIKE %s OR year LIKE %s OR gender LIKE %s
                """, (f"%{query}%",) * 6)

            student_data = cur.fetchall()
            cur.close()
            return student_data

        except Exception as e:
            print(f"Error searching students: {e}")
            return None


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
                INNER JOIN course ON course.code = student_info.course
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
