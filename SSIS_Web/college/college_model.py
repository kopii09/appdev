from flask_mysql_connector import MySQL

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
            # Check if the college with the given ID already exists
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM college WHERE `code` = %s", (code,))
            if cur.fetchone():
                print(f"College with ID '{code}' already exists.")
            else:
                # Insert a new college into the database
                cur.execute("INSERT INTO college (`code`, `name`) VALUES (%s, %s)",
                            (code, name))
                cls.mysql.connection.commit()
                print(f"College '{code}' has been added.")
        except Exception as e:
            print(f"Error adding college: {e}")
            
    @classmethod
    def delete_college(cls, code):
            cur = cls.mysql.connection.cursor()
            cur.execute("SELECT * FROM college WHERE `code` = %s", (code,))
            college = cur.fetchone()

            if college:
                # Delete the college from the database
                print("Deleting college with ID:", code)
                cur.execute("DELETE FROM college WHERE `code` = %s", (code,))
                cls.mysql.connection.commit()

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
            cur.execute("UPDATE college SET `code`=%s,  `name` = %s WHERE `code` = %s",
                        (new_code, name, old_code))
            cls.mysql.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating college: {e}")
        return False


    @classmethod
    def get_college_by_code(cls, code):
            cur = cls.mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT * FROM college WHERE `code` = %s", (code))
            college= cur.fetchone()
            print
            cur.close()
            return college