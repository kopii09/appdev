from flask_mysql_connector import MySQL

class CourseManager:
    def __init__(self, mysql):
        self.mysql = mysql

    @classmethod
    def init_db(cls, mysql):
        cls.mysql = mysql

    @classmethod
    def get_course_data(cls):
        cur = cls.mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM course")
        course_data = cur.fetchall()
        cur.close()

        return course_data

    @classmethod
    def get_colleges(cls):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT code, name FROM college")
            colleges = cur.fetchall()
            #print(courses)
            cur.close()
            return colleges
        except Exception as e:
            print(f"Error fetching college: {e}")
            return [] 
        
    @classmethod
    def add_course(cls, code, name, college):
        try:
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM course WHERE `code` = %s", (code,))
            if cur.fetchone():
                print(f"Course with ID '{code}' already exists.")
                return False  # <-- Proper failure indicator
            else:
                cur.execute("INSERT INTO course (`code`, `name`, `college`) VALUES (%s, %s, %s)",
                            (code, name, college))
                cls.mysql.connection.commit()
                print(f"Course '{code}' has been added.")
                return True  # <-- Success indicator
        except Exception as e:
            print(f"Error adding course: {e}")
            return False

            
    @classmethod
    def delete_course(cls, code):
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM course WHERE `code` = %s", (code,))
            course = cur.fetchone()

            if course:
                # Delete the course from the database
                print("Deleting course with ID:", code)
                cur.execute("DELETE FROM course WHERE `code` = %s", (code,))
                cls.mysql.connection.commit()

    @classmethod
    def search_courses(cls, field=None, query=None):
        cur = cls.mysql.connection.cursor(dictionary=True)

        if field != 'all':
            # Search by specific field
            cur.execute(f"SELECT * FROM course WHERE `{field}` LIKE %s", (f"%{query}%",))
        else:
            # Search by all columns
            cur.execute("SELECT * FROM course WHERE code LIKE %s OR name LIKE %s OR college LIKE %s",
                        (f"%{query}%", f"%{query}%", f"%{query}%"))

        course_data = cur.fetchall()
        cur.close()
        return course_data

    @classmethod
    def update_course(cls, old_code, new_code, name, college):
        try:
            print("Inside update_course")  # 👈 Log 1
            print("Old:", old_code, "| New:", new_code, "| Name:", name, "| College:", college)  # 👈 Log 2

            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM course WHERE `code` = %s", (new_code,))
            if cur.fetchone():
                if old_code == new_code:
                    print("Updating course — same code.")  # 👈 Log 3
                    pass
                else:
                    print(f"Duplicate code '{new_code}' exists.")  # 👈 Log 4
                    return Exception
            cur.execute("UPDATE course SET `code`=%s, `name`=%s, `college`=%s WHERE `code`=%s",
                        (new_code, name, college, old_code))
            cls.mysql.connection.commit()
            print("Update successful!")  # 👈 Log 5
            return True
        except Exception as e:
            print(f"Error updating course: {e}")
        return False



    @classmethod
    def get_course_by_code(cls, code):
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT * FROM course WHERE `code` = %s", (code))
            course= cur.fetchone()
            print
            cur.close()
            return course