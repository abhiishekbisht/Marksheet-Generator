#!/usr/bin/env python3
"""
Security Setup Script
Generates secure keys and validates configuration for production deployment
"""

import secrets
import os
import sys

def generate_secret_key():
    """Generate a cryptographically secure secret key"""
    return secrets.token_hex(32)

def check_env_file():
    """Check if .env file exists and has production-ready values"""
    if not os.path.exists('.env'):
        print("⚠️  WARNING: .env file not found!")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        
    warnings = []
    
    # Check for default/insecure values
    if 'gulzar-marksheet-secret-key-2024' in content:
        warnings.append("SECRET_KEY is using default value - MUST CHANGE!")
    
    if 'MYSQL_PASSWORD=' in content and ('MYSQL_PASSWORD=\n' in content or 'MYSQL_PASSWORD=newpassword' in content):
        warnings.append("MYSQL_PASSWORD is empty or using default - MUST CHANGE!")
    
    if 'FLASK_DEBUG=True' in content or 'FLASK_ENV=development' in content:
        warnings.append("Flask is in DEBUG/DEVELOPMENT mode - MUST CHANGE for production!")
    
    return warnings

def main():
    print("=" * 60)
    print("🔐 Marksheet Application - Security Setup")
    print("=" * 60)
    print()
    
    # Generate new secret key
    print("1. Generating new SECRET_KEY...")
    new_secret_key = generate_secret_key()
    print(f"   ✅ Generated: {new_secret_key}")
    print()
    
    # Check environment file
    print("2. Checking environment configuration...")
    warnings = check_env_file()
    
    if warnings:
        print("   ⚠️  SECURITY WARNINGS:")
        for warning in warnings:
            print(f"      - {warning}")
    else:
        print("   ✅ Environment configuration looks good!")
    print()
    
    # Production checklist
    print("3. Production Deployment Checklist:")
    print()
    print("   DATABASE SECURITY:")
    print("   [ ] Created production MySQL database")
    print("   [ ] Using strong database password")
    print("   [ ] Database accessible from hosting server")
    print("   [ ] Database backups configured")
    print()
    
    print("   APPLICATION SECURITY:")
    print("   [ ] Updated SECRET_KEY in .env (use generated key above)")
    print("   [ ] Set FLASK_ENV=production")
    print("   [ ] Set FLASK_DEBUG=False")
    print("   [ ] Changed default admin password after deployment")
    print("   [ ] Verified .env is in .gitignore")
    print("   [ ] Removed .env from git history if previously committed")
    print()
    
    print("   HOSTING CONFIGURATION:")
    print("   [ ] All environment variables set on hosting platform")
    print("   [ ] Static files properly configured")
    print("   [ ] Database initialized (ran init_db.py)")
    print("   [ ] HTTPS/SSL certificate configured")
    print("   [ ] Domain name configured (if applicable)")
    print()
    
    print("   POST-DEPLOYMENT:")
    print("   [ ] Tested login functionality")
    print("   [ ] Tested marksheet creation")
    print("   [ ] Tested PDF generation")
    print("   [ ] Tested file uploads")
    print("   [ ] Verified all pages load correctly")
    print("   [ ] Changed default credentials")
    print()
    
    print("=" * 60)
    print("📝 NEXT STEPS:")
    print("=" * 60)
    print()
    print("1. Copy the generated SECRET_KEY above")
    print("2. Update your .env file with:")
    print(f"   SECRET_KEY={new_secret_key}")
    print("   FLASK_ENV=production")
    print("   FLASK_DEBUG=False")
    print()
    print("3. Update database credentials with production values")
    print()
    print("4. Review DEPLOYMENT_GUIDE.md for hosting instructions")
    print()
    print("5. Never commit .env file to git!")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
