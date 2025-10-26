# Production Deployment Checklist

## ✅ Pre-Deployment Security

- [ ] **SECRET_KEY Changed**: Run `python security_setup.py` and update `.env`
- [ ] **Database Credentials**: Update all MySQL credentials in `.env`
- [ ] **Debug Mode OFF**: Set `FLASK_DEBUG=False` and `FLASK_ENV=production`
- [ ] **.env Not Committed**: Verify `.env` is in `.gitignore` and not in git history
- [ ] **Default Passwords**: Plan to change admin/teacher passwords after deployment
- [ ] **.env.example Updated**: Ensure it has NO real credentials (only placeholders)

## 🗄️ Database Setup

- [ ] **Production Database Created**: MySQL database ready on hosting platform
- [ ] **Connection Tested**: Can connect to database remotely
- [ ] **Credentials Noted**: Host, username, password, database name recorded
- [ ] **Backup Strategy**: Know how to backup/restore database

## 📦 Code Preparation

- [ ] **Dependencies Listed**: All packages in `requirements.txt`
- [ ] **Gunicorn Added**: `gunicorn` in `requirements.txt` (already done ✅)
- [ ] **Procfile Created**: For Heroku deployment (already done ✅)
- [ ] **Git Repository**: Code committed and pushed to Git
- [ ] **Static Files**: Logo and uploads folder structure correct

## 🚀 Hosting Platform Setup

Choose ONE hosting option and complete its checklist:

### Option A: Heroku
- [ ] Heroku account created
- [ ] Heroku CLI installed
- [ ] App created: `heroku create your-app-name`
- [ ] MySQL addon added: `heroku addons:create cleardb:ignite` or `jawsdb:kitefin`
- [ ] Environment variables set: `heroku config:set KEY=value`
- [ ] Deployed: `git push heroku main`
- [ ] Database initialized: `heroku run python init_db.py`

### Option B: PythonAnywhere
- [ ] PythonAnywhere account created
- [ ] Code uploaded or cloned from Git
- [ ] Virtual environment created and dependencies installed
- [ ] MySQL database created in PythonAnywhere
- [ ] Web app configured (WSGI file)
- [ ] Static files mapped
- [ ] `.env` file created with production values
- [ ] Database initialized: `python init_db.py`

### Option C: Railway.app
- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] MySQL database service added
- [ ] Environment variables configured
- [ ] Automatic deployment triggered

### Option D: VPS (DigitalOcean/Linode)
- [ ] Server created and accessed via SSH
- [ ] MySQL installed and configured
- [ ] Database and user created
- [ ] Application code deployed
- [ ] Virtual environment set up
- [ ] Gunicorn configured as systemd service
- [ ] Nginx configured as reverse proxy
- [ ] SSL certificate installed (Certbot)
- [ ] Firewall configured

## 🔒 Post-Deployment Security

- [ ] **Application Accessible**: Can access via URL
- [ ] **Login Works**: Admin and teacher logins functional
- [ ] **Change Admin Password**: Logged in and changed from `admin123`
- [ ] **Change Teacher Password**: Changed from `teacher123` or remove teacher account
- [ ] **Test All Features**: Create marksheet, generate PDF, upload files
- [ ] **HTTPS Enabled**: Site accessible via https:// (SSL certificate)
- [ ] **Secure Cookies**: Session cookies secure over HTTPS

## 📊 Monitoring & Maintenance

- [ ] **Logging Configured**: Know how to check application logs
- [ ] **Error Monitoring**: Set up error notifications
- [ ] **Database Backups**: Automated backups scheduled
- [ ] **Update Plan**: Know how to deploy updates
- [ ] **Downtime Plan**: Know how to restore if issues occur

## 🧪 Final Testing

- [ ] **Login**: Test admin and teacher login
- [ ] **Create Marksheet**: Fill form and submit
- [ ] **View Result**: Verify marks display correctly
- [ ] **Generate PDF**: Download and verify PDF quality
- [ ] **Verify Marksheet**: Enter roll number and verify
- [ ] **History Page**: View all marksheets (admin)
- [ ] **Clear Data**: Test admin clear all data button (optional)
- [ ] **Upload Logo**: Test logo upload functionality
- [ ] **Mobile View**: Test responsive design on mobile
- [ ] **Print/Save**: Test print functionality

## 📚 Documentation

- [ ] **Credentials Saved Securely**: Database and admin credentials stored safely (NOT in git)
- [ ] **Deployment URL Noted**: Application URL recorded
- [ ] **Hosting Dashboard Access**: Know how to access hosting provider dashboard
- [ ] **Support Info**: Know where to get help (hosting provider docs)

## ⚠️ Common Issues Checklist

- [ ] **Static files not loading**: Check static files configuration
- [ ] **Database connection fails**: Verify credentials and host accessibility
- [ ] **500 errors**: Check application logs for details
- [ ] **Upload fails**: Check upload folder permissions and size limits
- [ ] **PDF generation fails**: Verify reportlab and PIL installed correctly

---

## 🎯 Quick Start for Heroku (Recommended)

```bash
# 1. Install Heroku CLI (macOS)
brew tap heroku/brew && brew install heroku

# 2. Login
heroku login

# 3. Create app
cd /Users/datalynx/Desktop/mg/marksheet_app
heroku create your-marksheet-app

# 4. Add MySQL
heroku addons:create cleardb:ignite

# 5. Set environment variables
python security_setup.py  # Get new SECRET_KEY
heroku config:set SECRET_KEY="your-new-secret-key"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

# Get database URL and parse it
heroku config:get CLEARDB_DATABASE_URL
# Format: mysql://user:password@host/database
# Set individual variables:
heroku config:set MYSQL_HOST="host-from-url"
heroku config:set MYSQL_USER="user-from-url"
heroku config:set MYSQL_PASSWORD="password-from-url"
heroku config:set MYSQL_DATABASE="database-from-url"

# 6. Deploy
git add .
git commit -m "Ready for production"
git push heroku main

# 7. Initialize database
heroku run python init_db.py

# 8. Open app
heroku open

# 9. Check logs
heroku logs --tail
```

---

## 🆘 Emergency Contacts

- **Heroku Support**: https://help.heroku.com/
- **PythonAnywhere Forum**: https://www.pythonanywhere.com/forums/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **MySQL Documentation**: https://dev.mysql.com/doc/

---

**Remember**: 
1. NEVER commit `.env` file
2. ALWAYS change default passwords
3. ALWAYS use HTTPS in production
4. ALWAYS backup your database regularly

**Good luck! 🚀**
