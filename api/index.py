"""
Vercel Serverless Function Entry Point
This file wraps the Flask app for Vercel deployment
"""

import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a variable named 'app' or a handler function
# For Flask, we can use the app directly
handler = app

# This is required for Vercel
if __name__ == "__main__":
    app.run()
