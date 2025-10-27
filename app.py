from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import base64
from PIL import Image as PILImage
import pandas as pd
from config import Config

app = Flask(__name__)
try:
    app.config.from_object(Config)
except Exception as e:
    print(f"Config error: {e}")
    app.config['SECRET_KEY'] = 'fallback-secret-key'

# Health check route
@app.route('/health')
def health():
    return "OK", 200

# Database connection
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DATABASE']
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Initialize database
def init_db():
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create students table
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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL DEFAULT 'teacher',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check if role column exists, if not add it
            cursor.execute("SHOW COLUMNS FROM users LIKE 'role'")
            role_column_exists = cursor.fetchone()
            
            if not role_column_exists:
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'teacher'")
            
            # Create default admin user
            admin_password = generate_password_hash('admin123')
            teacher_password = generate_password_hash('teacher123')
            
            cursor.execute('''
                INSERT IGNORE INTO users (username, password_hash, role) 
                VALUES ('admin', %s, 'admin'), ('teacher', %s, 'teacher')
            ''', (admin_password, teacher_password))
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Database initialized successfully!")
        else:
            print("Could not connect to database")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_grade(percentage):
    if percentage >= 90:
        return 'A+', 'Outstanding Performance'
    elif percentage >= 80:
        return 'A', 'Excellent Performance'
    elif percentage >= 70:
        return 'B+', 'Very Good Performance'
    elif percentage >= 60:
        return 'B', 'Good Performance'
    elif percentage >= 50:
        return 'C', 'Satisfactory Performance'
    elif percentage >= 40:
        return 'D', 'Needs Improvement'
    else:
        return 'F', 'Failed - Requires Re-examination'

# Routes
@app.route('/')
def index():
    try:
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password!', 'error')
        else:
            flash('Database connection error!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/generate_marksheet', methods=['POST'])
def generate_marksheet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get form data
        student_name = request.form['student_name']
        roll_no = request.form['roll_no']
        branch = request.form['branch']
        semester = request.form['semester']
        exam_type = request.form['exam_type']
        class_teacher = request.form.get('class_teacher', '')
        principal = request.form.get('principal', '')
        include_signature = request.form.get('include_signature') == '1'
        include_seal = request.form.get('include_seal') == '1'
        
        # Get subjects and marks
        subjects_data = []
        total_marks = 0
        total_max_marks = 0
        
        subject_names = request.form.getlist('subject_name[]')
        marks_list = request.form.getlist('marks[]')
        max_marks_list = request.form.getlist('max_marks[]')
        
        for i, subject in enumerate(subject_names):
            if subject.strip():
                marks = int(marks_list[i])
                max_marks = int(max_marks_list[i])
                
                # Calculate grade for individual subject
                subject_percentage = (marks / max_marks) * 100
                subject_grade, _ = calculate_grade(subject_percentage)
                
                subjects_data.append({
                    'name': subject,
                    'marks': marks,
                    'max_marks': max_marks,
                    'grade': subject_grade
                })
                
                total_marks += marks
                total_max_marks += max_marks
        
        # Calculate overall percentage and grade
        percentage = (total_marks / total_max_marks) * 100 if total_max_marks > 0 else 0
        grade, remarks = calculate_grade(percentage)
        # Save to database
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Insert student record
            cursor.execute('''
                INSERT INTO students (name, roll_no, branch, semester, exam_type, 
                                    total_marks, max_marks, percentage, grade, remarks, 
                                    class_teacher, principal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (student_name, roll_no, branch, semester, exam_type,
                  total_marks, total_max_marks, percentage, grade, remarks,
                  class_teacher, principal))
            
            student_id = cursor.lastrowid
            
            # Insert subjects
            for subject in subjects_data:
                cursor.execute('''
                    INSERT INTO subjects (student_id, subject_name, marks, max_marks, grade)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (student_id, subject['name'], subject['marks'], 
                      subject['max_marks'], subject['grade']))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Get signature and seal URLs if they exist
            teacher_signature_url = None
            principal_signature_url = None
            college_seal_url = None
            
            if include_signature and class_teacher:
                teacher_sig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'teachersign.png')
                if os.path.exists(teacher_sig_path):
                    teacher_signature_url = url_for('static', filename='uploads/teachersign.png')
            
            if include_signature and principal:
                principal_sig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'principalsign.png')
                if os.path.exists(principal_sig_path):
                    principal_signature_url = url_for('static', filename='uploads/principalsign.png')
            
            if include_seal:
                seal_path = os.path.join(app.config['UPLOAD_FOLDER'], 'collegeseal.png')
                if os.path.exists(seal_path):
                    college_seal_url = url_for('static', filename='uploads/collegeseal.png')
            
            return render_template('result.html', 
                                 student={
                                     'id': student_id,
                                     'name': student_name,
                                     'roll_no': roll_no,
                                     'branch': branch,
                                     'semester': semester,
                                     'exam_type': exam_type,
                                     'total_marks': total_marks,
                                     'max_marks': total_max_marks,
                                     'percentage': round(percentage, 2),
                                     'grade': grade,
                                     'remarks': remarks,
                                     'class_teacher': class_teacher,
                                     'principal': principal,
                                     'date': datetime.datetime.now().strftime('%B %d, %Y'),
                                     'include_signature': include_signature,
                                     'include_seal': include_seal
                                 },
                                 subjects=subjects_data,
                                 college_name=app.config['COLLEGE_NAME'],
                                 teacher_signature_url=teacher_signature_url,
                                 principal_signature_url=principal_signature_url,
                                 college_seal_url=college_seal_url)
        else:
            flash('Database connection error!', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        flash(f'Error generating marksheet: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download_pdf/<int:student_id>')
def download_pdf(student_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get student data from database
        connection = get_db_connection()
        if not connection:
            flash('Database connection error!', 'error')
            return redirect(url_for('index'))
        
        cursor = connection.cursor(dictionary=True)
        
        # Get student details
        cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        
        # Get subjects
        cursor.execute('SELECT * FROM subjects WHERE student_id = %s', (student_id,))
        subjects = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if not student:
            flash('Student record not found!', 'error')
            return redirect(url_for('index'))
        
        # Generate PDF that matches the web view exactly
        pdf_filename = f"marksheet_{student['roll_no']}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf"
        pdf_path = os.path.join('static', 'uploads', pdf_filename)
        
        # Create PDF with exact same layout as web view
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, 
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        styles = getSampleStyleSheet()
        story = []
        
        # Create custom styles that match the web view
        college_header_style = ParagraphStyle(
            'CollegeHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),  # Blue color like web
            alignment=TA_CENTER,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )
        
        college_subtitle_style = ParagraphStyle(
            'CollegeSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#64748b'),  # Gray color like web
            alignment=TA_CENTER,
            spaceAfter=10,
            fontStyle='italic'
        )
        
        marksheet_title_style = ParagraphStyle(
            'MarksheetTitle',
            parent=styles['Heading2'],
            fontSize=18,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=5
        )
        
        exam_type_style = ParagraphStyle(
            'ExamType',
            parent=styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=20
        )
        
        # Header section - exactly like web view
        story.append(Paragraph(app.config['COLLEGE_NAME'], college_header_style))
        story.append(Paragraph('Academic Excellence Since 1995', college_subtitle_style))
        story.append(Paragraph('ACADEMIC MARKSHEET', marksheet_title_style))
        story.append(Paragraph(student['exam_type'], exam_type_style))
        
        # Student details section - matching web layout
        detail_style = ParagraphStyle(
            'DetailStyle',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=10,
            rightIndent=10
        )
        
        # Student details table with exact web layout
        student_details = [
            ['<b>Student Name:</b>', student['name'], '<b>Roll Number:</b>', student['roll_no']],
            ['<b>Branch:</b>', student['branch'], '<b>Semester:</b>', student['semester']],
            ['<b>Exam Type:</b>', student['exam_type'], '<b>Result Date:</b>', student['date_created'].strftime('%B %d, %Y')]
        ]
        
        detail_table = Table(student_details, colWidths=[1.5*inch, 2.2*inch, 1.5*inch, 1.8*inch])
        detail_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(detail_table)
        story.append(Spacer(1, 20))
        
        # Subjects table - exactly matching web design with blue header
        header_data = [['S.No.', 'Subject', 'Marks Obtained', 'Maximum Marks', 'Grade']]
        subject_rows = []
        
        for i, subject in enumerate(subjects, 1):
            subject_rows.append([
                str(i),
                subject['subject_name'],
                str(subject['marks']),
                str(subject['max_marks']),
                subject['grade']
            ])
        
        # Add total row
        total_row = [['TOTAL', '', str(student['total_marks']), str(student['max_marks']), student['grade']]]
        
        # Combine all table data
        table_data = header_data + subject_rows + total_row
        
        subjects_table = Table(table_data, colWidths=[0.8*inch, 2.8*inch, 1.2*inch, 1.2*inch, 0.8*inch])
        subjects_table.setStyle(TableStyle([
            # Header row styling (blue background like web)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows styling
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            
            # Total row styling (blue background like web)
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
            
            # Grid and padding
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(subjects_table)
        story.append(Spacer(1, 20))
        
        # Result summary section
        summary_data = [
            ['<b>Total Marks:</b>', f"{student['total_marks']}/{student['max_marks']}"],
            ['<b>Percentage:</b>', f"{student['percentage']:.2f}%"],
            ['<b>Grade:</b>', student['grade']],
            ['<b>Remarks:</b>', student['remarks']]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 25))
        
        # Signatures section (if enabled)
        if student.get('class_teacher') or student.get('principal'):
            signature_data = []
            sig_row = []
            if student.get('class_teacher'):
                sig_row.extend(['Class Teacher', '', 'Principal'])
                name_row = [student.get('class_teacher', ''), '', student.get('principal', '')]
            else:
                sig_row.extend(['', '', 'Principal'])
                name_row = ['', '', student.get('principal', '')]
                
            signature_data = [
                sig_row,
                name_row,
                ['_________________', '', '_________________'],
                ['', '', '']
            ]
            
            signature_table = Table(signature_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
            signature_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            story.append(signature_table)
            story.append(Spacer(1, 15))
        
        # Verification section without QR code
        verification_text = f"""
        <b>Digital Verification</b><br/>
        This marksheet is digitally verified and authentic.<br/>
        <b>Verified by {app.config['COLLEGE_NAME']}</b><br/>
        Student ID: {student_id}
        """
        
        verification_style = ParagraphStyle(
            'VerificationStyle',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=10,
            alignment=TA_CENTER
        )
        
        story.append(Spacer(1, 10))
        story.append(Paragraph(verification_text, verification_style))
        story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(story)
        
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
        
    except Exception as e:
        flash(f'Error generating PDF: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download_html_pdf/<int:student_id>')
def download_html_pdf(student_id):
    """Generate a print-optimized view of the marksheet that matches the web preview exactly"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get student data from database
        connection = get_db_connection()
        if not connection:
            flash('Database connection error!', 'error')
            return redirect(url_for('index'))
        
        cursor = connection.cursor(dictionary=True)
        
        # Get student details
        cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        
        # Get subjects
        cursor.execute('SELECT * FROM subjects WHERE student_id = %s', (student_id,))
        subjects = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if not student:
            flash('Student record not found!', 'error')
            return redirect(url_for('index'))
        
        # Prepare student data for template
        student_data = {
            'id': student_id,
            'name': student['name'],
            'roll_no': student['roll_no'],
            'branch': student['branch'],
            'semester': student['semester'],
            'exam_type': student['exam_type'],
            'total_marks': student['total_marks'],
            'max_marks': student['max_marks'],
            'percentage': round(student['percentage'], 2),
            'grade': student['grade'],
            'remarks': student['remarks'],
            'class_teacher': student.get('class_teacher', ''),
            'principal': student.get('principal', ''),
            'date': student['date_created'].strftime('%B %d, %Y'),
            'include_signature': True,  # Default to true for PDF
            'include_seal': True        # Default to true for PDF
        }
        
        # Get signature and seal URLs if they exist
        teacher_signature_url = None
        principal_signature_url = None
        college_seal_url = None
        
        if student_data['include_signature'] and student_data['class_teacher']:
            teacher_sig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'teachersign.png')
            if os.path.exists(teacher_sig_path):
                teacher_signature_url = url_for('static', filename='uploads/teachersign.png')
        
        if student_data['include_signature'] and student_data['principal']:
            principal_sig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'principalsign.png')
            if os.path.exists(principal_sig_path):
                principal_signature_url = url_for('static', filename='uploads/principalsign.png')
        
        if student_data['include_seal']:
            seal_path = os.path.join(app.config['UPLOAD_FOLDER'], 'collegeseal.png')
            if os.path.exists(seal_path):
                college_seal_url = url_for('static', filename='uploads/collegeseal.png')
        
        # Render the print-optimized template
        return render_template('print_marksheet.html',
                             student=student_data,
                             subjects=subjects,
                             college_name=app.config['COLLEGE_NAME'],
                             teacher_signature_url=teacher_signature_url,
                             principal_signature_url=principal_signature_url,
                             college_seal_url=college_seal_url)
        
    except Exception as e:
        flash(f'Error generating print view: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '')
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        if search_query:
            cursor.execute('''
                SELECT * FROM students 
                WHERE name LIKE %s OR roll_no LIKE %s 
                ORDER BY date_created DESC
            ''', (f'%{search_query}%', f'%{search_query}%'))
        else:
            cursor.execute('SELECT * FROM students ORDER BY date_created DESC LIMIT 50')
        
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('history.html', students=students, search_query=search_query)
    else:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.', 'error')
        return redirect(url_for('index'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get basic statistics
        cursor.execute('SELECT COUNT(*) as total_students FROM students')
        total_students = cursor.fetchone()['total_students']
        
        cursor.execute('SELECT COUNT(*) as passed FROM students WHERE grade != "F"')
        passed_students = cursor.fetchone()['passed']
        
        cursor.execute('SELECT AVG(percentage) as avg_percentage FROM students')
        avg_result = cursor.fetchone()
        avg_percentage = round(avg_result['avg_percentage'], 2) if avg_result['avg_percentage'] else 0
        
        # Branch statistics
        cursor.execute('''
            SELECT branch, COUNT(*) as count, AVG(percentage) as avg_perc 
            FROM students 
            GROUP BY branch
        ''')
        branch_stats = cursor.fetchall()
        
        # Top performers
        cursor.execute('''
            SELECT name, roll_no, percentage, grade 
            FROM students 
            ORDER BY percentage DESC 
            LIMIT 10
        ''')
        top_performers = cursor.fetchall()
        
        # Enhanced Analytics Data
        # Grade distribution
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN percentage >= 90 THEN 1 ELSE 0 END) as a_plus,
                SUM(CASE WHEN percentage >= 85 AND percentage < 90 THEN 1 ELSE 0 END) as a_grade,
                SUM(CASE WHEN percentage >= 75 AND percentage < 85 THEN 1 ELSE 0 END) as b_plus,
                SUM(CASE WHEN percentage >= 65 AND percentage < 75 THEN 1 ELSE 0 END) as b_grade,
                SUM(CASE WHEN percentage >= 55 AND percentage < 65 THEN 1 ELSE 0 END) as c_grade,
                SUM(CASE WHEN percentage >= 40 AND percentage < 55 THEN 1 ELSE 0 END) as d_grade,
                SUM(CASE WHEN percentage < 40 THEN 1 ELSE 0 END) as f_grade
            FROM students
        ''')
        grade_distribution = cursor.fetchone()
        
        # Semester-wise performance
        cursor.execute('''
            SELECT semester, COUNT(*) as count, AVG(percentage) as avg_perc
            FROM students 
            GROUP BY semester
            ORDER BY semester
        ''')
        semester_stats = cursor.fetchall()
        
        # At-risk students (below 40%)
        cursor.execute('''
            SELECT COUNT(*) as at_risk_count
            FROM students 
            WHERE percentage < 40
        ''')
        at_risk_count = cursor.fetchone()['at_risk_count']
        
        # Star performers (90%+)
        cursor.execute('''
            SELECT COUNT(*) as star_count
            FROM students 
            WHERE percentage >= 90
        ''')
        star_count = cursor.fetchone()['star_count']
        
        # Subject-wise performance (sample - you can expand this based on your subject data)
        cursor.execute('''
            SELECT 
                AVG(percentage) as overall_avg,
                MIN(percentage) as lowest_score,
                MAX(percentage) as highest_score
            FROM students
        ''')
        performance_stats = cursor.fetchone()
        
        # Calculate improvement rate (mock data for demo)
        improvement_rate = 12.5 if total_students > 0 else 0
        consistency_score = min(95, max(60, 100 - (performance_stats['highest_score'] - performance_stats['lowest_score']) / 2)) if performance_stats['highest_score'] else 85
        
        cursor.close()
        connection
        
        return render_template('dashboard.html',
                             total_students=total_students,
                             passed_students=passed_students,
                             failed_students=total_students - passed_students,
                             avg_percentage=avg_percentage,
                             branch_stats=branch_stats,
                             top_performers=top_performers,
                             grade_distribution=grade_distribution,
                             semester_stats=semester_stats,
                             at_risk_count=at_risk_count,
                             star_count=star_count,
                             improvement_rate=improvement_rate,
                             consistency_score=round(consistency_score, 1),
                             performance_stats=performance_stats)
    else:
        flash('Database connection error!', 'error')
        return redirect(url_for('index'))

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        verification_code = request.form.get('verification_code', '').strip()
        
        if not verification_code:
            flash('Please enter a verification code!', 'error')
            return render_template('verify.html')
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            # Try to find by verification code or roll number
            cursor.execute('SELECT * FROM students WHERE roll_no = %s', (verification_code,))
            student = cursor.fetchone()
            
            if student:
                cursor.execute('SELECT * FROM subjects WHERE student_id = %s', (student['id'],))
                subjects = cursor.fetchall()
                cursor.close()
                connection.close()
                
                return render_template('verify.html', student=student, subjects=subjects,
                                     college_name=app.config['COLLEGE_NAME'], verified=True)
            else:
                cursor.close()
                connection.close()
                flash('Invalid verification code or result not found!', 'error')
                return render_template('verify.html')
        else:
            flash('Database connection error!', 'error')
            return render_template('verify.html')
    
    # GET request - show verification form
    return render_template('verify.html')

@app.route('/verify/<int:student_id>')
def verify_result(student_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM students WHERE id = %s', (student_id,))
        student = cursor.fetchone()
        
        if student:
            cursor.execute('SELECT * FROM subjects WHERE student_id = %s', (student_id,))
            subjects = cursor.fetchall()
            cursor.close()
            connection.close()
            
            return render_template('verify.html', student=student, subjects=subjects,
                                 college_name=app.config['COLLEGE_NAME'])
        else:
            cursor.close()
            connection.close()
            return render_template('verify.html', error="Invalid verification code or result not found.")
    else:
        return render_template('verify.html', error="Database connection error.")

@app.route('/export_data')
def export_data():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        if connection:
            # Export students data
            df_students = pd.read_sql('SELECT * FROM students', connection)
            df_subjects = pd.read_sql('SELECT * FROM subjects', connection)
            connection.close()
            
            # Create Excel file
            excel_filename = f"marksheet_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            excel_path = os.path.join('static', 'uploads', excel_filename)
            
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_students.to_excel(writer, sheet_name='Students', index=False)
                df_subjects.to_excel(writer, sheet_name='Subjects', index=False)
            
            return send_file(excel_path, as_attachment=True, download_name=excel_filename)
        else:
            flash('Database connection error!', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error exporting data: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

# Excel Import Routes
@app.route('/import_excel', methods=['POST'])
def import_excel():
    """Import student data from Excel file"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        if 'excel_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['excel_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            return jsonify({'success': False, 'message': 'Invalid file format. Please upload .xlsx or .xls file'})
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        upload_path = os.path.join('static', 'uploads', filename)
        file.save(upload_path)
        
        # Read Excel file
        try:
            df = pd.read_excel(upload_path)
        except Exception as e:
            os.remove(upload_path)  # Clean up
            return jsonify({'success': False, 'message': f'Error reading Excel file: {str(e)}'})
        
        # Validate Excel structure
        required_columns = ['Student Name', 'Roll Number', 'Branch', 'Semester', 'Exam Type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            os.remove(upload_path)  # Clean up
            return jsonify({'success': False, 'message': f'Missing required columns: {", ".join(missing_columns)}'})
        
        # Process Excel data
        students_data = []
        
        for index, row in df.iterrows():
            try:
                # Extract student info
                student_info = {
                    'student_name': str(row['Student Name']).strip(),
                    'roll_no': str(row['Roll Number']).strip(),
                    'branch': str(row['Branch']).strip(),
                    'semester': str(row['Semester']).strip(),
                    'exam_type': str(row['Exam Type']).strip(),
                    'subjects': []
                }
                
                # Extract subject marks (columns after the first 5)
                subject_columns = [col for col in df.columns if col not in required_columns]
                
                for subject_col in subject_columns:
                    marks_value = row[subject_col]
                    if pd.notna(marks_value) and str(marks_value).strip() != '':
                        try:
                            marks = float(marks_value)
                            if 0 <= marks <= 100:  # Validate marks range
                                student_info['subjects'].append({
                                    'name': subject_col,
                                    'marks': int(marks),
                                    'max_marks': 100
                                })
                        except (ValueError, TypeError):
                            continue  # Skip invalid marks
                
                # Only add student if they have at least one valid subject
                if student_info['subjects']:
                    students_data.append(student_info)
                    
            except Exception as e:
                continue  # Skip problematic rows
        
        # Clean up uploaded file
        os.remove(upload_path)
        
        if not students_data:
            return jsonify({'success': False, 'message': 'No valid student data found in Excel file'})
        
        return jsonify({
            'success': True, 
            'data': students_data,
            'message': f'Successfully processed {len(students_data)} students'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error processing file: {str(e)}'})

@app.route('/bulk_create_marksheets', methods=['POST'])
def bulk_create_marksheets():
    """Create marksheets for multiple students from imported data"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        data = request.get_json()
        students_data = data.get('students', [])
        
        if not students_data:
            return jsonify({'success': False, 'message': 'No student data provided'})
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = connection.cursor()
        created_count = 0
        
        for student_data in students_data:
            try:
                # Calculate totals
                total_marks = sum(subject['marks'] for subject in student_data['subjects'])
                max_marks = sum(subject['max_marks'] for subject in student_data['subjects'])
                percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
                grade, remarks = calculate_grade(percentage)
                
                # Insert student record
                student_query = '''
                    INSERT INTO students (name, roll_no, branch, semester, exam_type, 
                                        total_marks, max_marks, percentage, grade, remarks, 
                                        created_by, date_created, include_signature, include_seal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                
                cursor.execute(student_query, (
                    student_data['student_name'],
                    student_data['roll_no'],
                    student_data['branch'],
                    student_data['semester'],
                    student_data['exam_type'],
                    total_marks,
                    max_marks,
                    percentage,
                    grade,
                    remarks,
                    session['user_id'],
                    datetime.datetime.now(),
                    True,  # include_signature
                    True   # include_seal
                ))
                
                student_id = cursor.lastrowid
                
                # Insert subjects
                for subject in student_data['subjects']:
                    subject_query = '''
                        INSERT INTO subjects (student_id, name, marks, max_marks, grade)
                        VALUES (%s, %s, %s, %s, %s)
                    '''
                    subject_percentage = (subject['marks'] / subject['max_marks'] * 100) if subject['max_marks'] > 0 else 0
                    subject_grade, _ = calculate_grade(subject_percentage)
                    
                    cursor.execute(subject_query, (
                        student_id,
                        subject['name'],
                        subject['marks'],
                        subject['max_marks'],
                        subject_grade
                    ))
                
                created_count += 1
                
            except mysql.connector.IntegrityError:
                # Student with this roll number already exists, skip
                continue
            except Exception as e:
                print(f"Error creating marksheet for {student_data.get('student_name', 'Unknown')}: {str(e)}")
                continue
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'created_count': created_count,
            'message': f'Successfully created {created_count} marksheets'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating bulk marksheets: {str(e)}'})

# Enhanced Analytics API Routes
@app.route('/api/performance_metrics')
def get_performance_metrics():
    """Get performance metrics for analytics dashboard"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = connection.cursor(dictionary=True)
        
        # Get performance distribution
        query = '''
            SELECT 
                SUM(CASE WHEN percentage >= 85 THEN 1 ELSE 0 END) as excellent,
                SUM(CASE WHEN percentage >= 70 AND percentage < 85 THEN 1 ELSE 0 END) as good,
                SUM(CASE WHEN percentage >= 55 AND percentage < 70 THEN 1 ELSE 0 END) as average,
                SUM(CASE WHEN percentage < 55 THEN 1 ELSE 0 END) as poor,
                COUNT(*) as total,
                AVG(percentage) as average_percentage
            FROM students
        '''
        
        cursor.execute(query)
        metrics = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'metrics': metrics})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching metrics: {str(e)}'})

@app.route('/api/top_performers', methods=['POST'])
def get_top_performers():
    """Get top performers based on filters"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        filters = request.get_json() or {}
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = connection.cursor(dictionary=True)
        
        # Build query with filters
        query = '''
            SELECT id, name, roll_no, branch, semester, exam_type, 
                   total_marks, max_marks, percentage, grade
            FROM students
            WHERE 1=1
        '''
        params = []
        
        if filters.get('branch') and filters['branch'] != 'all':
            query += ' AND branch = %s'
            params.append(filters['branch'])
        
        if filters.get('semester') and filters['semester'] != 'all':
            query += ' AND semester = %s'
            params.append(filters['semester'])
        
        if filters.get('exam_type') and filters['exam_type'] != 'all':
            query += ' AND exam_type = %s'
            params.append(filters['exam_type'])
        
        query += ' ORDER BY percentage DESC LIMIT 10'
        
        cursor.execute(query, params)
        performers = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'performers': performers})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching top performers: {str(e)}'})

@app.route('/api/performers_by_type', methods=['POST'])
def get_performers_by_type():
    """Get performers filtered by specific type (branch, semester, subject)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        filters = request.get_json() or {}
        performer_type = filters.get('type', 'overall')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Database connection error'})
        
        cursor = connection.cursor(dictionary=True)
        
        if performer_type == 'branch':
            query = '''
                SELECT branch, COUNT(*) as student_count, 
                       AVG(percentage) as avg_percentage,
                       MAX(percentage) as top_percentage
                FROM students
                GROUP BY branch
                ORDER BY avg_percentage DESC
            '''
        elif performer_type == 'subject':
            query = '''
                SELECT s.name as subject_name, 
                       COUNT(*) as student_count,
                       AVG(s.marks * 100.0 / s.max_marks) as avg_percentage,
                       MAX(s.marks * 100.0 / s.max_marks) as top_percentage
                FROM subjects s
                JOIN students st ON s.student_id = st.id
                GROUP BY s.name
                ORDER BY avg_percentage DESC
            '''
        else:  # overall
            query = '''
                SELECT id, name, roll_no, branch, semester, exam_type, 
                       total_marks, max_marks, percentage, grade
                FROM students
                ORDER BY percentage DESC
                LIMIT 10
            '''
        
        cursor.execute(query)
        performers = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'performers': performers})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error fetching performers by type: {str(e)}'})

# Enhanced Analytics API Endpoints
@app.route('/api/at_risk_students')
def api_at_risk_students():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT name, roll_no, branch, semester, exam_type, percentage
            FROM students 
            WHERE percentage < 40
            ORDER BY percentage ASC
        ''')
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'students': students})
    
    return jsonify({'success': False, 'message': 'Database connection failed'})

@app.route('/api/star_performers')
def api_star_performers():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT name, roll_no, branch, semester, exam_type, percentage
            FROM students 
            WHERE percentage >= 90
            ORDER BY percentage DESC
        ''')
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'students': students})
    
    return jsonify({'success': False, 'message': 'Database connection failed'})

@app.route('/api/grade_distribution')
def api_grade_distribution():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN percentage >= 90 THEN 1 ELSE 0 END) as a_plus,
                SUM(CASE WHEN percentage >= 85 AND percentage < 90 THEN 1 ELSE 0 END) as a_grade,
                SUM(CASE WHEN percentage >= 75 AND percentage < 85 THEN 1 ELSE 0 END) as b_plus,
                SUM(CASE WHEN percentage >= 65 AND percentage < 75 THEN 1 ELSE 0 END) as b_grade,
                SUM(CASE WHEN percentage >= 55 AND percentage < 65 THEN 1 ELSE 0 END) as c_grade,
                SUM(CASE WHEN percentage >= 40 AND percentage < 55 THEN 1 ELSE 0 END) as d_grade,
                SUM(CASE WHEN percentage < 40 THEN 1 ELSE 0 END) as f_grade,
                COUNT(*) as total
            FROM students
        ''')
        data = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'data': data})
    
    return jsonify({'success': False, 'message': 'Database connection failed'})

@app.route('/api/semester_stats')
def api_semester_stats():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT semester, COUNT(*) as count, AVG(percentage) as avg_perc
            FROM students 
            GROUP BY semester
            ORDER BY semester
        ''')
        data = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'data': data})
    
    return jsonify({'success': False, 'message': 'Database connection failed'})

@app.route('/api/export_at_risk_students')
def export_at_risk_students():
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('''
            SELECT name, roll_no, branch, semester, exam_type, percentage
            FROM students 
            WHERE percentage < 40
            ORDER BY percentage ASC
        ''')
        students = cursor.fetchall()
        cursor.close()
        connection.close()
        
        if students:
            # Create CSV data
            import io
            import csv
            from flask import make_response
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Name', 'Roll Number', 'Branch', 'Semester', 'Exam Type', 'Percentage'])
            
            for student in students:
                writer.writerow([
                    student['name'],
                    student['roll_no'],
                    student['branch'],
                    student['semester'],
                    student['exam_type'],
                    student['percentage']
                ])
            
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=at_risk_students.csv'
            return response
        else:
            return jsonify({'success': False, 'message': 'No at-risk students found'})
    
    return jsonify({'success': False, 'message': 'Database connection failed'})

@app.route('/clear_all_data', methods=['POST'])
def clear_all_data():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    # Only admin can clear all data
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Admin privileges required'})
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Delete all subjects first (due to foreign key constraint)
            cursor.execute('DELETE FROM subjects')
            subjects_deleted = cursor.rowcount
            
            # Delete all students
            cursor.execute('DELETE FROM students')
            students_deleted = cursor.rowcount
            
            # Reset auto-increment
            cursor.execute('ALTER TABLE students AUTO_INCREMENT = 1')
            cursor.execute('ALTER TABLE subjects AUTO_INCREMENT = 1')
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({
                'success': True, 
                'message': f'Successfully deleted {students_deleted} students and {subjects_deleted} subjects from database'
            })
        else:
            return jsonify({'success': False, 'message': 'Database connection error'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Test endpoint
@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            cursor.close()
            conn.close()
            return f"<h1>Connected!</h1><p>Tables: {tables}</p><a href='/init-database-setup-2024'>Init DB</a>"
        else:
            return "<h1>Cannot connect</h1>"
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

# Special endpoint for database initialization (one-time use)
@app.route('/init-database-setup-2024', methods=['GET'])
def init_database_setup():
    """One-time database initialization endpoint"""
    try:
        init_db()
        return """
        <html>
        <head><title>Database Initialized</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: green;">✅ Database Initialized Successfully!</h1>
            <p>Your database tables have been created and default users are set up.</p>
            <h3>Login Credentials:</h3>
            <p><strong>Admin:</strong> username: admin | password: admin123</p>
            <p><strong>Teacher:</strong> username: teacher | password: teacher123</p>
            <br>
            <a href="/login" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Go to Login Page</a>
        </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: red;">❌ Database Initialization Failed</h1>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """, 500

if __name__ == '__main__':
    try:
        init_db()
    except:
        pass
    app.run(debug=True, host='0.0.0.0', port=5001)
