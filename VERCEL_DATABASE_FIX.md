# Vercel Database Connection Fix

## Problem
Your app is showing "Database connection error!" because Vercel doesn't provide MySQL hosting.

## Solution: Use Cloud MySQL Database

### Option 1: PlanetScale (Recommended - Free Tier)

1. **Sign up at PlanetScale**
   - Go to https://planetscale.com
   - Create free account
   - Create new database (e.g., `marksheet_db`)

2. **Get Connection Details**
   - Click on database
   - Go to "Connect"
   - Select "Connect with: MySQL"
   - Copy the credentials:
     - Host
     - Username
     - Password
     - Database name

3. **Add to Vercel Environment Variables**
   - Go to: https://vercel.com/dashboard
   - Select your project
   - Go to Settings → Environment Variables
   - Add these variables:

   ```
   MYSQL_HOST=your-planetscale-host.us-east-1.psdb.cloud
   MYSQL_USER=your-username
   MYSQL_PASSWORD=your-password
   MYSQL_DATABASE=marksheet_db
   SECRET_KEY=your-secret-key-change-this
   FLASK_ENV=production
   FLASK_DEBUG=False
   COLLEGE_NAME=GULZAR GROUP OF INSTITUTIONS
   COLLEGE_ADDRESS=Academic Excellence Since 1995
   ```

4. **Redeploy**
   - After adding variables, redeploy your app
   - Or push a new commit to trigger deployment

### Option 2: Railway (Free Tier)

1. **Sign up at Railway**
   - Go to https://railway.app
   - Create account
   - Create new project
   - Add MySQL database

2. **Get Connection String**
   - Click on MySQL service
   - Copy connection details
   - Format: `host`, `user`, `password`, `database`

3. **Add to Vercel** (same as above)

### Option 3: AWS RDS (More Complex, Paid)

1. Create RDS MySQL instance
2. Configure security groups
3. Get connection details
4. Add to Vercel environment variables

## Quick Fix for Testing (Not Recommended for Production)

If you want to test quickly, you can:

1. **Use SQLite Instead** (requires code changes)
   - Easier for Vercel
   - But requires modifying your Flask app

2. **Deploy on Different Platform**
   - Use **Railway** or **Render** which provide MySQL
   - These platforms are better for full-stack apps with databases

## After Setting Up Database

### Initialize Database Tables
After connecting to cloud MySQL, you need to run:

```bash
# Connect to your cloud MySQL and run init_db.py
python init_db.py
```

Or manually create tables using the MySQL console of your cloud provider.

## Recommended: Use Railway Instead of Vercel

Railway is better suited for your Flask + MySQL app:

1. Go to https://railway.app
2. Create new project
3. Add MySQL database (automatic)
4. Deploy your Flask app
5. Railway handles both app and database!

Would you like help with any of these options?
