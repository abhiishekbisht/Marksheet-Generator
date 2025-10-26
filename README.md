# 🎓 Student Marksheet Generator

A professional Flask-based web application for generating, managing, and verifying student marksheets.

## ✨ Features

- **Generate Marksheets**: Create professional marksheets with subjects, marks, and grades
- **Bulk Import**: Import student data from Excel files
- **History Management**: View and search previously generated marksheets
- **Verification System**: Verify marksheet authenticity using unique codes
- **Admin Dashboard**: Analytics and performance overview
- **PDF Export**: Print and save marksheets as PDF
- **Multi-user Support**: Separate admin and teacher roles
- **Production Ready**: Configured for deployment to Heroku, PythonAnywhere, or VPS

## 🚀 Quick Start

### Local Development

#### Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

#### Installation

1. **Clone or download the project**
   ```bash
   cd /path/to/marksheet_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database**
   - Edit `config.py` with your MySQL credentials
   - Or set environment variables in `.env`

4. **Initialize database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   # Windows
   start.bat
   
   # Mac/Linux
   ./start.sh
   # or
   python app.py
   ```

6. **Access the application**
   - Open browser: `http://127.0.0.1:5001`

### 🌐 Production Deployment

Ready to host your application? See our comprehensive guides:

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete step-by-step instructions for:
  - Heroku (Recommended for beginners)
  - PythonAnywhere (Free tier available)
  - Railway.app (Modern alternative)
  - DigitalOcean/VPS (Full control)

- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Essential security and deployment checklist

#### Quick Deploy to Heroku

```bash
# Run automated deployment script
./deploy_heroku.sh

# Or manual deployment:
heroku create your-app-name
heroku addons:create cleardb:ignite
python security_setup.py  # Get secure SECRET_KEY
heroku config:set SECRET_KEY="your-generated-key"
heroku config:set FLASK_ENV=production
git push heroku main
heroku run python init_db.py
```

#### Security Setup

Before deploying, **ALWAYS** run:

```bash
python security_setup.py
```

This will:
- Generate a secure SECRET_KEY
- Check for insecure default values
- Provide a production checklist

## 🔐 Default Login Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Teacher Account:**
- Username: `teacher`
- Password: `teacher123`

⚠️ **Change these passwords after first login!**

## 📁 Project Structure

```
marksheet_app/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── init_db.py            # Database initialization
├── requirements.txt       # Python dependencies
├── start.bat             # Windows startup script
├── start.sh              # Unix startup script
├── static/               # Static files (CSS, JS, images)
│   ├── style.css
│   ├── script.js
│   └── uploads/          # Uploaded files
├── templates/            # HTML templates
│   ├── index.html        # Generate marksheet
│   ├── result.html       # Display marksheet
│   ├── verify.html       # Verify marksheet
│   ├── history.html      # View history
│   ├── dashboard.html    # Admin dashboard
│   └── login.html        # Login page
└── README.md
```

## 🎯 Usage

### Generate a Marksheet

1. Login with your credentials
2. Go to **Generate** page
3. Fill in student details and marks
4. Click **Generate Marksheet**
5. View, print, or save as PDF

### Import from Excel

1. On Generate page, click **Close Excel Import**
2. Upload Excel file with format:
   - Columns: Student Name, Roll Number, Branch, Semester, Exam Type, Subject1, Subject2...
3. Click **Import Data**

### Verify a Marksheet

1. Go to **Verify** page
2. Enter verification code (shown on marksheet)
3. View authenticated marksheet

### View History

1. Go to **History** page
2. Search by student name or roll number
3. View or regenerate past marksheets

### Admin Dashboard (Admin only)

1. Login as admin
2. Go to **Dashboard**
3. View analytics, statistics, and performance charts

## ⚙️ Configuration

Edit `config.py` or create `.env` file:

```python
# Database
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DATABASE = 'marksheet_db'

# College Info
COLLEGE_NAME = 'Your College Name'

# Session
SECRET_KEY = 'your-secret-key-here'
```

## 🗑️ Clear Data

**Admin users can clear all marksheet data:**
1. Go to History page
2. Click **🗑️ Clear All Data** button
3. Confirm twice to delete all records

## 📊 Database Schema

**Tables:**
- `students` - Student information and results
- `subjects` - Individual subject marks
- `users` - Login credentials

## 🛠️ Troubleshooting

**Database Connection Error:**
- Check MySQL is running
- Verify credentials in `config.py`
- Ensure database exists (run `init_db.py`)

**Port Already in Use:**
- Change port in `app.py`: `app.run(port=5001)`

**Import Errors:**
- Install missing packages: `pip install -r requirements.txt`

## 📄 License

This project is for educational purposes.

## 🔒 Security Notes

**IMPORTANT for Production:**
1. **Never commit `.env` file** - Contains sensitive credentials
2. **Change default passwords** - Update admin/teacher passwords immediately
3. **Use HTTPS** - Enable SSL certificate for production
4. **Strong SECRET_KEY** - Run `python security_setup.py` to generate
5. **Database backups** - Schedule regular backups of your database
6. **Keep updated** - Regularly update dependencies: `pip list --outdated`

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete hosting instructions
- **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)** - Pre-deployment checklist
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Quick reference guide
- **[CLEANUP_SUMMARY.md](CLEANUP_SUMMARY.md)** - Project cleanup history

## 👨‍💻 Support

For issues or questions:
- Check the deployment guides
- Review security_setup.py output
- Consult your hosting provider's documentation

---

**Version:** 2.0  
**Last Updated:** December 2024  
**Status:** Production Ready ✅
# Marksheet-Generator
