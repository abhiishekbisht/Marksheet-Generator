#!/usr/bin/env python3
"""
Railway Database Initialization Script
Run this to initialize your Railway MySQL database
"""

import mysql.connector
from werkzeug.security import generate_password_hash
import os

# Railway MySQL credentials (from environment variables)
db_config = {
    'host': 'mysql.railway.internal',
    'user': 'root',
    'password': 'heeQVOlWIrjFCHrgksUYRSekZdhmWyDA',
    'database': 'railway'
}

print("=" * 60)
print("RAILWAY DATABASE INITIALIZATION")
print("=" * 60)
print(f"Host: {db_config['host']}")
print(f"Database: {db_config['database']}")
print(f"User: {db_config['user']}")
print("=" * 60)

try:
    # Connect to MySQL
    print("\n📡 Connecting to Railway MySQL...")
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    
    print("✅ Connected successfully!")
    
    # Drop existing tables (for clean setup)
    print("\n🗑️  Dropping existing tables (if any)...")
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0')
    cursor.execute('DROP TABLE IF EXISTS subjects')
    cursor.execute('DROP TABLE IF EXISTS students')
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('SET FOREIGN_KEY_CHECKS = 1')
    print("✅ Old tables removed")
    
    # Create students table
    print("\n📝 Creating students table...")
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
    print("✅ Students table created")
    
    # Create subjects table
    print("\n📚 Creating subjects table...")
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
    print("✅ Subjects table created")
    
    # Create users table
    print("\n👥 Creating users table...")
    cursor.execute('''
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'teacher',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Users table created")
    
    # Create default users
    print("\n🔐 Creating default users...")
    admin_password = generate_password_hash('admin123')
    teacher_password = generate_password_hash('teacher123')
    
    cursor.execute('''
        INSERT INTO users (username, password_hash, role) 
        VALUES ('admin', %s, 'admin'), ('teacher', %s, 'teacher')
    ''', (admin_password, teacher_password))
    
    connection.commit()
    print("✅ Default users created")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 60)
    print("🎉 DATABASE INITIALIZED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📱 Your app is live at:")
    print("🌐 https://web-production-835dc.up.railway.app")
    print("\n🔑 Login Credentials:")
    print("   👑 Admin:   username: admin   | password: admin123")
    print("   👨‍🏫 Teacher: username: teacher | password: teacher123")
    print("\n" + "=" * 60)
    
except mysql.connector.Error as err:
    print(f"\n❌ Database Error: {err}")
    exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
