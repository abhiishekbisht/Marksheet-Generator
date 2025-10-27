import mysql.connector
from werkzeug.security import generate_password_hash

# Direct Railway MySQL connection
conn = mysql.connector.connect(
    host='mysql.railway.internal',
    user='root',
    password='heeQVOlWIrjFCHrgksUYRSekZdhmWyDA',
    database='railway'
)

cursor = conn.cursor()

print("Creating tables...")

# Drop and recreate tables
cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
cursor.execute('DROP TABLE IF EXISTS subjects')
cursor.execute('DROP TABLE IF EXISTS students')  
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('SET FOREIGN_KEY_CHECKS = 1')

# Students table
cursor.execute('''
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    roll_no VARCHAR(50) UNIQUE NOT NULL,
    branch VARCHAR(100) NOT NULL,
    semester VARCHAR(20) NOT NULL,
    exam_type VARCHAR(50) NOT NULL,
    total_marks INT NOT NULL,
    max_marks INT NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    grade VARCHAR(10) NOT NULL,
    remarks TEXT,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    class_teacher VARCHAR(255),
    principal VARCHAR(255)
)
''')

# Subjects table
cursor.execute('''
CREATE TABLE subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject_name VARCHAR(255) NOT NULL,
    marks INT NOT NULL,
    max_marks INT NOT NULL,
    grade VARCHAR(10),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
)
''')

# Users table
cursor.execute('''
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'teacher',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Insert default users
admin_pwd = generate_password_hash('admin123')
teacher_pwd = generate_password_hash('teacher123')

cursor.execute(
    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    ('admin', admin_pwd, 'admin')
)
cursor.execute(
    "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
    ('teacher', teacher_pwd, 'teacher')
)

conn.commit()
cursor.close()
conn.close()

print("✅ Database initialized successfully!")
print("Login: admin/admin123 or teacher/teacher123")
