from flask_mysql_connector import MySQL
import mysql.connector
from mysql.connector import errorcode


class CollegeManager:
    def __init__(self, mysql):
        self.mysql = mysql

    @classmethod
    def init_db(cls, mysql):
        cls.mysql = mysql

    @classmethod
    def get_college_data(cls):
        cur = cls.mysql.connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM college")
        college_data = cur.fetchall()
        cur.close()

        return college_data

    @classmethod
    def get_colleges(cls):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT code, name FROM college")
            colleges = cur.fetchall()
            #print(colleges)
            cur.close()
            return colleges
        except Exception as e:
            print(f"Error fetching college: {e}")
            return [] 
        
    @classmethod
    def add_college(cls, code, name):
        try:
            cur = cls.mysql.connection.cursor()
            # Check if the college with the given code already exists
            cur.execute("SELECT * FROM college WHERE `code` = %s", (code,))
            if cur.fetchone():
                # Duplicate found
                return {'status': 'error', 'message': f"College with code '{code}' already exists."}
            
            # Insert new college
            cur.execute("INSERT INTO college (`code`, `name`) VALUES (%s, %s)", (code, name))
            cls.mysql.connection.commit()
            return {'status': 'success', 'message': f"College '{code}' has been added."}
        except Exception as e:
            return {'status': 'error', 'message': f"Error adding college: {e}"}

            
    @classmethod
    def delete_college(cls, code):
        try:
            cur = cls.mysql.connection.cursor()

            # Disassociate students from the college
            cur.execute("UPDATE student_info SET college = NULL WHERE college = %s", (code,))
            
            # Disassociate courses from the college (if you have a college field in the course table)
            cur.execute("UPDATE course SET college = NULL WHERE college = %s", (code,))
            
            # Now delete the college
            cur.execute("DELETE FROM college WHERE code = %s", (code,))
            
            cls.mysql.connection.commit()
            print(f"College {code} deleted successfully.")

        except Exception as e:
            print(f"Error deleting college: {e}")

        finally:
            cur.close()


    @classmethod
    def search_colleges(cls, field=None, query=None):
        cur = cls.mysql.connection.cursor(dictionary=True)

        if field != 'all':
            # Search by specific field
            cur.execute(f"SELECT * FROM college WHERE `{field}` LIKE %s", (f"%{query}%",))
        else:
            # Search by all columns
            cur.execute("SELECT * FROM college WHERE code LIKE %s OR name LIKE %s",
                        (f"%{query}%", f"%{query}%"))

        college_data = cur.fetchall()
        cur.close()
        return college_data
    
    @classmethod
    def update_college(cls, old_code, new_code, name):
        try:
            cur = cls.mysql.connection.cursor()
            cur.execute("UPDATE college SET code=%s, name=%s WHERE code=%s", (new_code, name, old_code))
            cls.mysql.connection.commit()
            return {'status': 'success'}
        except mysql.connector.IntegrityError as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                return {'status': 'error', 'message': f'College code {new_code} already exists.'}
            raise
        except Exception as e:
            print(f"Error updating college: {e}")
            return {'status': 'error', 'message': 'Unexpected error updating college.'}
    
    @classmethod
    def get_college_by_code(cls, code):
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT * FROM college WHERE `code` = %s", (code,))
            college= cur.fetchone()
            print
            cur.close()
            return college
    
    @classmethod
    def get_college_data_paginated(cls, page, per_page):
        offset = (page - 1) * per_page
        query = "SELECT code, name FROM college LIMIT %s OFFSET %s"
        cursor = cls.mysql.connection.cursor(dictionary=True)
        cursor.execute(query, (per_page, offset))
        results = cursor.fetchall()
        cursor.close()
        return results


    @classmethod
    def count_colleges(cls):
        try:
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) AS count FROM college")
            count = cur.fetchone()['count']
            cur.close()
            return count
        except Exception as e:
            print(f"Error counting colleges: {e}")
            return 0
