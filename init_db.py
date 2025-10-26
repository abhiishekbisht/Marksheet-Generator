#!/usr/bin/env python3
"""
Database initialization script for Student Marksheet Generator
"""

import mysql.connector
import sys
from werkzeug.security import generate_password_hash

def create_database():
    """Create the marksheet database"""
    print("🔧 Initializing database...")
    
    # Try to connect to MySQL without specifying a database first
    try:
        # Try connection without password first
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        print("✅ Connected to MySQL successfully")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            # Ask for password if access denied
            password = input("Enter MySQL root password: ")
            try:
                connection = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password=password
                )
                print("✅ Connected to MySQL successfully")
            except mysql.connector.Error as err2:
                print(f"❌ Failed to connect to MySQL: {err2}")
                return False
        else:
            print(f"❌ Failed to connect to MySQL: {err}")
            return False
    
    cursor = connection.cursor()
    
    try:
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS marksheet_db")
        print("✅ Database 'marksheet_db' created successfully")
        
        # Switch to the database
        cursor.execute("USE marksheet_db")
        
        # Create students table
        print("📋 Creating students table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
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
        
        # Create subjects table
        print("📋 Creating subjects table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                subject_name VARCHAR(255) NOT NULL,
                marks INT NOT NULL,
                max_marks INT NOT NULL,
                grade VARCHAR(10),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
        ''')
        
        # Create users table
        print("📋 Creating users table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'teacher',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default users
        print("👤 Creating default users...")
        admin_password = generate_password_hash('admin123')
        teacher_password = generate_password_hash('teacher123')
        
        cursor.execute('''
            INSERT IGNORE INTO users (username, password_hash, role) 
            VALUES ('admin', %s, 'admin'), ('teacher', %s, 'teacher')
        ''', (admin_password, teacher_password))
        
        connection.commit()
        print("✅ Default users created (admin/admin123, teacher/teacher123)")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nLogin credentials:")
        print("Admin: username='admin', password='admin123'")
        print("Teacher: username='teacher', password='teacher123'")
        
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")
        cursor.close()
        connection.close()
        return False

if __name__ == "__main__":
    success = create_database()
    if not success:
        sys.exit(1)
