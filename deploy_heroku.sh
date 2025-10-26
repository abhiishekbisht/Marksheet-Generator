#!/bin/bash

# Quick Deployment Script for Heroku
# This script automates the Heroku deployment process

echo "======================================"
echo "Marksheet App - Heroku Deployment"
echo "======================================"
echo ""

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found!"
    echo "Install it with: brew tap heroku/brew && brew install heroku"
    exit 1
fi

echo "✅ Heroku CLI found"
echo ""

# Check if logged in
if ! heroku auth:whoami &> /dev/null; then
    echo "Please login to Heroku:"
    heroku login
fi

echo "✅ Logged in to Heroku"
echo ""

# Check if git repo is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit for deployment"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

echo ""
read -p "Enter your app name (or press Enter for auto-generated): " APP_NAME

# Create Heroku app
if [ -z "$APP_NAME" ]; then
    echo "Creating Heroku app with auto-generated name..."
    heroku create
else
    echo "Creating Heroku app: $APP_NAME..."
    heroku create "$APP_NAME"
fi

echo ""
echo "✅ Heroku app created"
echo ""

# Add MySQL database
echo "Adding MySQL database addon..."
read -p "Choose database addon (1=ClearDB, 2=JawsDB) [1]: " DB_CHOICE
DB_CHOICE=${DB_CHOICE:-1}

if [ "$DB_CHOICE" == "1" ]; then
    heroku addons:create cleardb:ignite
    DB_URL=$(heroku config:get CLEARDB_DATABASE_URL)
else
    heroku addons:create jawsdb:kitefin
    DB_URL=$(heroku config:get JAWSDB_URL)
fi

echo "✅ Database addon added"
echo ""

# Generate secret key
echo "Generating secure SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Set environment variables
echo "Setting environment variables..."
heroku config:set SECRET_KEY="$SECRET_KEY"
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=False

echo ""
echo "⚠️  IMPORTANT: Parse your database URL and set credentials:"
echo ""
echo "Database URL: $DB_URL"
echo ""
echo "Format: mysql://USER:PASSWORD@HOST/DATABASE"
echo ""
echo "Run these commands with your actual values:"
echo "heroku config:set MYSQL_HOST='your-host'"
echo "heroku config:set MYSQL_USER='your-user'"
echo "heroku config:set MYSQL_PASSWORD='your-password'"
echo "heroku config:set MYSQL_DATABASE='your-database'"
echo ""

read -p "Have you set the database credentials? (y/n): " DB_SET

if [ "$DB_SET" != "y" ]; then
    echo ""
    echo "Please set the database credentials before continuing."
    echo "Run the commands above, then re-run this script."
    exit 1
fi

# Deploy to Heroku
echo ""
echo "Deploying to Heroku..."
git push heroku main || git push heroku master

echo ""
echo "✅ Deployment complete"
echo ""

# Initialize database
echo "Initializing database..."
heroku run python init_db.py

echo ""
echo "======================================"
echo "🎉 Deployment Successful!"
echo "======================================"
echo ""
echo "Your app is now live!"
echo ""
echo "Next steps:"
echo "1. Open your app: heroku open"
echo "2. View logs: heroku logs --tail"
echo "3. Login with admin/admin123"
echo "4. CHANGE THE ADMIN PASSWORD IMMEDIATELY"
echo ""
echo "App URL: $(heroku info -s | grep web-url | cut -d= -f2)"
echo ""
