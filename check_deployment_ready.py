#!/usr/bin/env python3
"""
Pre-Deployment Validation Script
Checks if your project is ready for production deployment
"""

import os
import sys

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    if exists:
        print(f"  ✅ {filepath}")
        return True
    else:
        status = "❌" if required else "⚠️"
        print(f"  {status} {filepath} {'(REQUIRED)' if required else '(Optional)'}")
        return not required

def check_gitignore():
    """Check if .gitignore includes sensitive files"""
    if not os.path.exists('.gitignore'):
        print("  ❌ .gitignore not found (REQUIRED)")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    required_entries = ['.env', '__pycache__']
    missing = []
    
    for entry in required_entries:
        if entry not in content:
            missing.append(entry)
    
    # Check for *.pyc or *.py[cod] pattern
    if '*.pyc' not in content and '*.py[cod]' not in content:
        missing.append('*.pyc or *.py[cod]')
    
    if missing:
        print(f"  ⚠️ .gitignore missing entries: {', '.join(missing)}")
        return False
    
    print("  ✅ .gitignore properly configured")
    return True

def check_env_security():
    """Check if .env contains insecure values"""
    if not os.path.exists('.env'):
        print("  ⚠️ .env not found (create from .env.example)")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    issues = []
    
    # Check for default/insecure values
    if 'gulzar-marksheet-secret-key-2024' in content:
        issues.append("Default SECRET_KEY")
    
    if 'MYSQL_PASSWORD=' in content and ('MYSQL_PASSWORD=\n' in content or 'MYSQL_PASSWORD=newpassword' in content):
        issues.append("Weak/default database password")
    
    if 'FLASK_DEBUG=True' in content:
        issues.append("DEBUG mode enabled")
    
    if 'FLASK_ENV=development' in content:
        issues.append("Development environment")
    
    if issues:
        print(f"  ⚠️ Security issues in .env:")
        for issue in issues:
            print(f"     - {issue}")
        return False
    
    print("  ✅ .env file secure")
    return True

def check_requirements():
    """Check if requirements.txt has necessary packages"""
    if not os.path.exists('requirements.txt'):
        print("  ❌ requirements.txt not found (REQUIRED)")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = ['Flask', 'mysql-connector-python', 'gunicorn', 'python-dotenv']
    missing = []
    
    for package in required_packages:
        if package.lower() not in content.lower():
            missing.append(package)
    
    if missing:
        print(f"  ⚠️ Missing packages: {', '.join(missing)}")
        return False
    
    print("  ✅ requirements.txt complete")
    return True

def main():
    print("=" * 60)
    print("🔍 Pre-Deployment Validation")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Check required files
    print("1. Checking required files...")
    required_files = [
        'app.py',
        'config.py',
        'init_db.py',
        'requirements.txt',
        'Procfile',
        '.gitignore',
    ]
    
    for filepath in required_files:
        if not check_file_exists(filepath, required=True):
            all_passed = False
    print()
    
    # Check optional files
    print("2. Checking deployment files...")
    optional_files = [
        'DEPLOYMENT_GUIDE.md',
        'PRODUCTION_CHECKLIST.md',
        'HOSTING_READY.md',
        'runtime.txt',
        'deploy_heroku.sh',
    ]
    
    for filepath in optional_files:
        check_file_exists(filepath, required=False)
    print()
    
    # Check .gitignore
    print("3. Checking .gitignore configuration...")
    if not check_gitignore():
        all_passed = False
    print()
    
    # Check requirements.txt
    print("4. Checking dependencies...")
    if not check_requirements():
        all_passed = False
    print()
    
    # Check .env security
    print("5. Checking environment security...")
    if not check_env_security():
        all_passed = False
    print()
    
    # Check directory structure
    print("6. Checking directory structure...")
    required_dirs = ['static', 'static/uploads', 'templates']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ (REQUIRED)")
            all_passed = False
    print()
    
    # Check templates
    print("7. Checking templates...")
    templates = ['index.html', 'result.html', 'verify.html', 'history.html', 'dashboard.html', 'login.html']
    for template in templates:
        check_file_exists(f'templates/{template}', required=True)
    print()
    
    # Final summary
    print("=" * 60)
    if all_passed:
        print("✅ All checks passed!")
        print("=" * 60)
        print()
        print("Your project is ready for deployment!")
        print()
        print("Next steps:")
        print("1. Run: python3 security_setup.py")
        print("2. Update .env with generated SECRET_KEY")
        print("3. Choose hosting platform (see DEPLOYMENT_GUIDE.md)")
        print("4. Deploy using ./deploy_heroku.sh or manual steps")
        print()
        return 0
    else:
        print("⚠️ Some issues need attention")
        print("=" * 60)
        print()
        print("Please fix the issues marked with ❌ or ⚠️ above")
        print("Run this script again to verify")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())
