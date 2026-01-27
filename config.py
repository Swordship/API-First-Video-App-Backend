import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://new_user11:newuser11@custmer.vocvmkz.mongodb.net/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'video_app')  # Database name
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'fallback-secret-key-change-me')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Flask
    DEBUG = os.getenv('FLASK_ENV') == 'development'