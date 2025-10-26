# Deployment Guide - Marksheet Application

## 🚀 Quick Deployment Options

### Option 1: Heroku (Recommended for beginners)
### Option 2: PythonAnywhere (Free tier available)
### Option 3: DigitalOcean/VPS (For more control)
### Option 4: Railway.app (Modern alternative)

---

## 📋 Pre-Deployment Checklist

### 1. Security Check ✅
- [ ] Remove `.env` from repository
- [ ] Update `.env.production` with actual credentials
- [ ] Generate strong SECRET_KEY
- [ ] Change default admin password after first login
- [ ] Verify `.gitignore` includes `.env`

### 2. Database Preparation ✅
- [ ] Set up production MySQL database
- [ ] Note down: host, username, password, database name
- [ ] Ensure database allows remote connections

### 3. Code Preparation ✅
- [ ] All dependencies in `requirements.txt`
- [ ] Configuration uses environment variables
- [ ] Static files properly configured

---

## 🔧 Option 1: Deploy to Heroku

### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- Git installed

### Step-by-Step Instructions

#### 1. Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Verify installation
heroku --version
```

#### 2. Login to Heroku
```bash
heroku login
```

#### 3. Prepare Your Application
```bash
cd /Users/datalynx/Desktop/mg/marksheet_app

# Initialize git if not already done
git init
git add .
git commit -m "Prepare for deployment"
```

#### 4. Create Heroku App
```bash
# Create a new Heroku app
heroku create your-marksheet-app

# Or use auto-generated name
heroku create
```

#### 5. Add MySQL Database
```bash
# Add ClearDB MySQL (Free tier: 5MB storage)
heroku addons:create cleardb:ignite

# Or use JawsDB MySQL (Free tier: 5MB storage)
heroku addons:create jawsdb:kitefin

# Get database connection string
heroku config:get CLEARDB_DATABASE_URL
# or
heroku config:get JAWSDB_URL
```

#### 6. Configure Environment Variables
```bash
# Set configuration variables
heroku config:set SECRET_KEY="your-super-secret-random-key-here"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# If using ClearDB, parse the URL and set individual values
# ClearDB URL format: mysql://user:password@host/database?reconnect=true
heroku config:set MYSQL_HOST=your-host
heroku config:set MYSQL_USER=your-user
heroku config:set MYSQL_PASSWORD=your-password
heroku config:set MYSQL_DATABASE=your-database
```

#### 7. Deploy
```bash
# Push to Heroku
git push heroku main

# Or if your branch is 'master'
git push heroku master
```

#### 8. Initialize Database
```bash
# Run database initialization
heroku run python init_db.py

# Open your app
heroku open
```

#### 9. View Logs
```bash
# Monitor application logs
heroku logs --tail
```

---

## 🐍 Option 2: Deploy to PythonAnywhere

### Prerequisites
- PythonAnywhere account (free tier available)

### Step-by-Step Instructions

#### 1. Create Account
- Go to [www.pythonanywhere.com](https://www.pythonanywhere.com)
- Sign up for free beginner account

#### 2. Upload Code
Option A: Using Git
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/marksheet_app.git
cd marksheet_app
```

Option B: Manual Upload
- Use "Files" tab to upload your project folder

#### 3. Set Up MySQL Database
- Go to "Databases" tab
- Create a new MySQL database
- Note down: hostname, username, password

#### 4. Configure Virtual Environment
```bash
# In Bash console
cd marksheet_app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Configure Web App
- Go to "Web" tab
- Click "Add a new web app"
- Choose "Manual configuration"
- Select Python 3.10

#### 6. WSGI Configuration
- Click on WSGI configuration file
- Replace content with:
```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/marksheet_app'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import flask app
from app import app as application
```

#### 7. Set Environment Variables
- Create `.env` file in project directory with production values
- Or set in WSGI file directly (less secure)

#### 8. Static Files Configuration
- In Web tab, add static files mapping:
  - URL: `/static/`
  - Directory: `/home/yourusername/marksheet_app/static/`

#### 9. Initialize Database
```bash
# In Bash console
cd marksheet_app
source venv/bin/activate
python init_db.py
```

#### 10. Reload Web App
- Click green "Reload" button in Web tab

---

## 🌊 Option 3: Deploy to Railway.app

### Prerequisites
- Railway account
- GitHub account

### Step-by-Step Instructions

#### 1. Push to GitHub
```bash
cd /Users/datalynx/Desktop/mg/marksheet_app
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/marksheet_app.git
git push -u origin main
```

#### 2. Deploy on Railway
- Go to [railway.app](https://railway.app)
- Click "Start a New Project"
- Select "Deploy from GitHub repo"
- Choose your repository

#### 3. Add MySQL Database
- Click "New"
- Select "Database" → "MySQL"
- Railway will automatically provide connection details

#### 4. Configure Environment Variables
- Click on your web service
- Go to "Variables" tab
- Add:
  - `SECRET_KEY`: your-secret-key
  - `FLASK_ENV`: production
  - `FLASK_DEBUG`: False
  - Database variables (auto-populated from MySQL service)

#### 5. Deploy
- Railway automatically deploys on git push
- Monitor deployment in "Deployments" tab

---

## 💻 Option 4: Deploy to DigitalOcean/VPS

### Prerequisites
- VPS account (DigitalOcean, Linode, etc.)
- Domain name (optional)
- SSH access

### Step-by-Step Instructions

#### 1. Set Up Server
```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install python3 python3-pip python3-venv nginx mysql-server -y
```

#### 2. Set Up MySQL
```bash
# Secure MySQL installation
mysql_secure_installation

# Create database
mysql -u root -p
```

```sql
CREATE DATABASE marksheet_db;
CREATE USER 'marksheet_user'@'localhost' IDENTIFIED BY 'your-secure-password';
GRANT ALL PRIVILEGES ON marksheet_db.* TO 'marksheet_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Deploy Application
```bash
# Create application directory
mkdir -p /var/www/marksheet_app
cd /var/www/marksheet_app

# Clone or upload your code
git clone https://github.com/yourusername/marksheet_app.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 4. Configure Environment
```bash
# Create .env file
nano .env
# Add your production configuration
```

#### 5. Set Up Gunicorn
```bash
# Create systemd service
nano /etc/systemd/system/marksheet.service
```

```ini
[Unit]
Description=Gunicorn instance for Marksheet App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/marksheet_app
Environment="PATH=/var/www/marksheet_app/venv/bin"
ExecStart=/var/www/marksheet_app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
systemctl start marksheet
systemctl enable marksheet
```

#### 6. Configure Nginx
```bash
nano /etc/nginx/sites-available/marksheet
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /var/www/marksheet_app/static;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/marksheet /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 7. Set Up SSL (Optional but Recommended)
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate
certbot --nginx -d your-domain.com
```

---

## 🔐 Security Best Practices

### 1. Generate Strong SECRET_KEY
```python
# Run this in Python to generate a secure key
import secrets
print(secrets.token_hex(32))
```

### 2. Change Default Passwords
- Login as admin immediately after deployment
- Change default credentials
- Or update database directly:
```python
from werkzeug.security import generate_password_hash
# Use the hash in your database
```

### 3. Enable HTTPS
- Use SSL/TLS certificates
- Force HTTPS redirects
- Set secure cookie flags

### 4. Database Security
- Use strong passwords
- Restrict database access to application only
- Regular backups
- Keep database updated

### 5. Application Security
- Keep dependencies updated: `pip list --outdated`
- Use environment variables for all secrets
- Implement rate limiting (use Flask-Limiter)
- Add CSRF protection
- Sanitize user inputs

---

## 🔍 Post-Deployment Checklist

- [ ] Application accessible via URL
- [ ] Login with admin credentials works
- [ ] Database connection successful
- [ ] File uploads working
- [ ] Marksheet generation/PDF download works
- [ ] All pages load without errors
- [ ] Change default admin password
- [ ] Test all features thoroughly
- [ ] Set up monitoring/logging
- [ ] Configure backups
- [ ] Document production credentials securely

---

## 🆘 Troubleshooting

### Application won't start
- Check logs: `heroku logs --tail` or server logs
- Verify all environment variables are set
- Check database connection

### Database connection errors
- Verify database credentials
- Check if database allows remote connections
- Ensure correct hostname/port

### Static files not loading
- Check static file configuration
- Verify file paths
- Check server permissions

### 500 Internal Server Error
- Check application logs
- Verify all dependencies installed
- Check file permissions
- Review database migrations

---

## 📚 Additional Resources

- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/latest/deploying/)
- [Heroku Python Documentation](https://devcenter.heroku.com/articles/getting-started-with-python)
- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)

---

## 📞 Support

For issues or questions:
1. Check application logs
2. Review this guide
3. Consult hosting provider documentation
4. Check Flask/MySQL documentation

**Good luck with your deployment! 🚀**
