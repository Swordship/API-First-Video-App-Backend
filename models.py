from pymongo import MongoClient
from config import Config
from datetime import datetime

# Connect to MongoDB
client = MongoClient(Config.MONGODB_URI)
db = client.get_database(Config.MONGODB_DB_NAME)

# Collections
users_collection = db['users']
videos_collection = db['videos']

# Create indexes for better performance
users_collection.create_index('email', unique=True)  # Email must be unique
videos_collection.create_index('is_active')  # Query active videos faster

class User:
    """User model"""
    
    @staticmethod
    def create(name, email, password_hash):
        """Create a new user"""
        user_data = {
            'name': name,
            'email': email.lower(),  # Store emails in lowercase for consistency
            'password_hash': password_hash,
            'created_at': datetime.utcnow()
        }
        result = users_collection.insert_one(user_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return users_collection.find_one({'email': email.lower()})
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        from bson import ObjectId
        return users_collection.find_one({'_id': ObjectId(user_id)})

class Video:
    """Video model"""
    
    @staticmethod
    def get_active_videos(limit=2):
        """Get active videos (limited to 2 for dashboard)"""
        return list(videos_collection.find(
            {'is_active': True}
        ).limit(limit))
    
    @staticmethod
    def find_by_id(video_id):
        """Find video by ID"""
        from bson import ObjectId
        return videos_collection.find_one({'_id': ObjectId(video_id)})
    
    @staticmethod
    def create(title, description, youtube_id, thumbnail_url):
        """Create a new video"""
        video_data = {
            'title': title,
            'description': description,
            'youtube_id': youtube_id,
            'thumbnail_url': thumbnail_url,
            'is_active': True,
            'created_at': datetime.utcnow()
        }
        result = videos_collection.insert_one(video_data)
        return result.inserted_id