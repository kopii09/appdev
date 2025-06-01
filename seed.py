from faker import Faker
import random
import mysql.connector

fake = Faker()

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dabdab",
    database="ssisweb_db"
)
cursor = db.cursor()

genders = ['Male', 'Female', 'Non-binary', 'Transgender', 'Prefer not to say', 'Not listed']
courses = ['BSCA', 'BSIT', 'BSIS', 'BSPSYCH', 'BSCE', 'BSEE']
years = [1, 2, 3, 4]

for i in range(100):
    student_id = f"2022-{2300 + i}"
    firstname = fake.first_name()
    lastname = fake.last_name()
    gender = random.choice(genders)
    course = random.choice(courses)
    year = random.choice(years)

    query = """
        INSERT INTO student_info (id, firstname, lastname, year, gender, course)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (student_id, firstname, lastname, year, gender, course)

    try:
        cursor.execute(query, values)
        print(f" Added student {student_id}")
    except mysql.connector.errors.IntegrityError as e:
        print(f" Error: {e}")

db.commit()
cursor.close()
db.close()
