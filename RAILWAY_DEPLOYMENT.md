# Deploy Flask + MySQL App to Railway

## Why Railway?
- ✅ Supports MySQL database natively
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Easy environment variable management
- ✅ Perfect for Flask apps with databases

## Step-by-Step Deployment

### 1. Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub account
3. Verify your account

### 2. Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Select your repository: `abhishekgulzar/marksheet-generator`
4. Click **"Deploy Now"**

### 3. Add MySQL Database

1. In your project, click **"+ New"**
2. Select **"Database"** → **"Add MySQL"**
3. Railway automatically creates MySQL database
4. Connection details are auto-generated

### 4. Configure Environment Variables

Railway will ask you to add variables. Add these:

```env
# Database (Railway auto-fills these from MySQL service)
MYSQL_HOST=${{MySQL.MYSQL_PRIVATE_URL}}
MYSQL_USER=${{MySQL.MYSQL_USER}}
MYSQL_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
MYSQL_DATABASE=${{MySQL.MYSQL_DATABASE}}

# Flask Config
SECRET_KEY=your-secret-key-change-this-to-random-string
FLASK_ENV=production
FLASK_DEBUG=False

# College Info
COLLEGE_NAME=GULZAR GROUP OF INSTITUTIONS
COLLEGE_ADDRESS=Academic Excellence Since 1995

# Upload
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

**Note:** Railway can reference the MySQL service variables automatically using `${{MySQL.VARIABLE_NAME}}`

### 5. Initialize Database

After deployment, initialize your database tables:

1. Open Railway dashboard
2. Go to your Flask service
3. Click on **"Settings"** → **"Connect"**
4. Run this command in terminal:

```bash
railway run python init_db.py
```

Or use Railway's console to run SQL directly.

### 6. Deploy

1. Railway automatically deploys from your GitHub repo
2. Every push to main branch triggers new deployment
3. You'll get a URL like: `https://your-app.railway.app`

## Alternative: Quick Railway CLI Deployment

### Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway
```

### Login and Deploy
```bash
# Navigate to project directory
cd /Users/datalynx/Desktop/mg/marksheet_app

# Login to Railway
railway login

# Link to project (or create new)
railway init

# Add MySQL database
railway add --database mysql

# Deploy
railway up

# Initialize database
railway run python init_db.py

# Get deployment URL
railway domain
```

## Comparison: Vercel vs Railway

| Feature | Vercel | Railway |
|---------|--------|---------|
| MySQL Support | ❌ No (need external DB) | ✅ Built-in |
| Flask Support | ⚠️ Serverless only | ✅ Native |
| File Uploads | ⚠️ Temporary only | ✅ Persistent |
| Free Tier | ✅ Yes | ✅ Yes |
| Best For | Static sites, Next.js | Full-stack apps |
| Setup Complexity | High (for Flask+MySQL) | Low |

## Recommended: Use Railway

For your Flask + MySQL marksheet app, **Railway is the better choice** because:
1. Native MySQL support (no external database needed)
2. Persistent file storage
3. Easier configuration
4. Better suited for traditional web apps

## Next Steps

1. Create Railway account
2. Deploy from GitHub
3. Add MySQL database
4. Initialize tables with `init_db.py`
5. Your app will work perfectly!

Would you like help with the Railway deployment?
