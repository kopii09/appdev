from flask_mysql_connector import MySQL


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
            # Check if the student with the given ID already exists
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM student_info WHERE `id` = %s", (id,))
            if cur.fetchone():
                print(f"Student with ID '{id}' already exists.")
                return Exception
            else:
                # Insert a new student into the database
                cur.execute("INSERT INTO student_info (`pic`, `id`, `firstname`, `lastname`, `course`, `gender`, `year`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (pic, id, firstname, lastname, course, gender, year))
                cls.mysql.connection.commit()
                print(
                    f"Student '{firstname} {lastname}' with ID '{id}' has been added.")
        except Exception as e:
            print(f"Error adding student: {e}")

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
            print(old_id)
            cur.execute(
                "SELECT * FROM student_info WHERE `id` = %s AND `id` != %s", (new_id, old_id))
            if cur.fetchone():
                if old_id == new_id:
                    pass
                else:
                    print(f"Student with ID '{new_id}' already exists.")
                    return Exception
            else:
                # Update student info
                cur.execute("UPDATE student_info SET `pic`=%s, `id`=%s, `firstname` = %s, `lastname` = %s, `course` = %s, `gender` = %s, `year` = %s WHERE `id` = %s",
                            (pic, new_id, firstname, lastname, course, gender, year, old_id))
                cls.mysql.connection.commit()
                return True
        except Exception as e:
            print(f"Error updating student: {e}")
        return False

    @classmethod
    def get_student_by_id(cls, student_id):
        cur = cls.mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM student_info WHERE `id` = %s",
                    (student_id,))
        student = cur.fetchone()
        print
        cur.close()
        return student
