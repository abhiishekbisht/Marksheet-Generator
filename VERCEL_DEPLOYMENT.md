# Vercel Deployment Guide for Marksheet Application

## ⚠️ Important Notice

**Vercel has limitations for Flask applications:**
- Serverless functions have a 10-second execution timeout on free tier
- Database connections may timeout in serverless environment
- File uploads are limited in serverless functions
- Session storage needs external service

**Recommended Alternative:** Heroku or PythonAnywhere (better for Flask apps with databases)

---

## 🚀 If You Still Want to Deploy to Vercel

### Prerequisites
1. Vercel account (free): https://vercel.com/signup
2. Vercel CLI installed

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

Or on macOS:
```bash
brew install vercel-cli
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Configure Environment Variables

Before deploying, you need to set up environment variables in Vercel.

**Option A: Via Vercel Dashboard**
1. Go to https://vercel.com/dashboard
2. Select your project (or create new)
3. Go to Settings → Environment Variables
4. Add these variables:

```
SECRET_KEY=445d0756c989ce496548165f3b898cf9a32c17106d61793e7fa171ee949a4206
FLASK_ENV=production
FLASK_DEBUG=False
MYSQL_HOST=your-database-host
MYSQL_USER=your-database-user
MYSQL_PASSWORD=your-database-password
MYSQL_DATABASE=marksheet_db
```

**Option B: Via CLI (during deployment)**
Vercel will prompt you to add environment variables.

### Step 4: Deploy

```bash
cd /Users/datalynx/Desktop/mg/marksheet_app

# First deployment (will prompt for project setup)
vercel

# Or production deployment directly
vercel --prod
```

During first deployment, answer:
- Set up and deploy? **Y**
- Which scope? (select your account)
- Link to existing project? **N** (first time)
- Project name? **marksheet-app**
- In which directory is your code? **./**
- Override settings? **N**

### Step 5: Set Up Database

**⚠️ Important:** Vercel doesn't include a database. You need:

**Option 1: Use PlanetScale (MySQL)**
```bash
# Install PlanetScale CLI
brew install planetscale/tap/pscale

# Create database
pscale database create marksheet-db

# Get connection string
pscale connect marksheet-db main

# Add to Vercel environment variables
```

**Option 2: Use Railway MySQL**
1. Go to https://railway.app
2. Create new project → Add MySQL
3. Copy connection details
4. Add to Vercel environment variables

**Option 3: Use External MySQL (DigitalOcean, AWS RDS, etc.)**

### Step 6: Initialize Database

After deployment, you need to run init_db.py once:

```bash
# This won't work on Vercel directly
# You need to connect to your database manually and run SQL

# Or use a temporary local connection:
python init_db.py  # with production database credentials
```

### Step 7: Access Your Application

```bash
# Get your deployment URL
vercel ls

# Or from deployment output
# URL format: https://marksheet-app-username.vercel.app
```

---

## ⚠️ Known Limitations on Vercel

### 1. **Serverless Timeouts**
- Free tier: 10 seconds per request
- Pro tier: 60 seconds per request
- **Issue:** PDF generation and complex queries may timeout

### 2. **File Storage**
- Vercel filesystem is read-only
- Uploaded files (logos) won't persist
- **Solution:** Use external storage (AWS S3, Cloudinary)

### 3. **Session Storage**
- Flask sessions won't work properly
- **Solution:** Use external Redis or database sessions

### 4. **Cold Starts**
- First request may be slow
- Database connection overhead

### 5. **Database Connection Pooling**
- May hit connection limits
- **Solution:** Use connection pooling library

---

## 🔧 Required Modifications for Vercel

If you want full functionality on Vercel, you need to modify:

### 1. File Uploads
Replace local file storage with cloud storage:

```python
# Instead of saving to static/uploads/
# Use AWS S3, Cloudinary, or Vercel Blob
import cloudinary
cloudinary.uploader.upload(file)
```

### 2. Session Management
Use database or Redis sessions:

```python
from flask_session import Session
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url(os.environ.get('REDIS_URL'))
```

### 3. Database Connection
Add connection pooling:

```python
from mysql.connector import pooling

connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)
```

---

## 📊 Vercel vs Alternatives Comparison

| Feature | Vercel | Heroku | PythonAnywhere |
|---------|--------|--------|----------------|
| **Flask Support** | Limited | Excellent | Excellent |
| **Database** | External | Add-on | Built-in |
| **File Uploads** | External | Yes | Yes |
| **Sessions** | External | Yes | Yes |
| **Timeout** | 10-60s | 30s | None |
| **Free Tier** | Yes | Limited | Yes |
| **Setup Complexity** | High | Medium | Easy |
| **Best For** | Static/Serverless | Full Apps | Python Apps |

---

## 🎯 Recommended Approach

### For This Application, We Recommend:

**1st Choice: Heroku** (Already configured!)
```bash
./deploy_heroku.sh
```
- Full Flask support
- MySQL addon available
- File uploads work
- Sessions work out of box

**2nd Choice: PythonAnywhere**
- See DEPLOYMENT_GUIDE.md
- Free tier available
- Perfect for Python/Flask
- Built-in MySQL

**3rd Choice: Railway**
- Modern alternative to Heroku
- Easy deployment
- Good Flask support

**Vercel:** Only if you modify the app for serverless architecture

---

## 🚀 Quick Vercel Deployment (Basic)

If you want to try Vercel anyway:

```bash
cd /Users/datalynx/Desktop/mg/marksheet_app

# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Set environment variables via dashboard first
# Then deploy
vercel --prod

# Note: You'll need external database and storage
```

---

## 📝 Post-Deployment Tasks

If you deploy to Vercel:

1. ✅ Set all environment variables
2. ✅ Set up external MySQL database
3. ✅ Initialize database tables
4. ✅ Configure external file storage (S3/Cloudinary)
5. ✅ Set up Redis for sessions (optional)
6. ✅ Test all features
7. ✅ Monitor for timeout errors

---

## 🆘 Troubleshooting

### "Function exceeded timeout"
- Move to Heroku or increase Vercel Pro limits
- Optimize database queries
- Use caching

### "Cannot write to filesystem"
- Use external storage for uploads
- Don't rely on local file system

### "Session not persisting"
- Use database or Redis sessions
- Configure SESSION_TYPE properly

### "Database connection failed"
- Check connection string
- Ensure database allows external connections
- Use connection pooling

---

## 💡 Final Recommendation

**For this marksheet application, Heroku is the best choice because:**
- ✅ Full Flask support
- ✅ MySQL database included
- ✅ File uploads work natively
- ✅ No timeout issues
- ✅ Already configured (see deploy_heroku.sh)
- ✅ Better for database-heavy apps

**Deploy to Heroku instead:**
```bash
./deploy_heroku.sh
```

Or follow: `DEPLOYMENT_GUIDE.md`

---

**Created:** October 27, 2025  
**Status:** Vercel deployment possible but not recommended for this app type
