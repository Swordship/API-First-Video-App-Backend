from models import videos_collection
from datetime import datetime

def seed_videos():
    """Seed database with 2 test videos"""
    
    print("=" * 50)
    print("🌱 Seeding database with test videos...")
    print("=" * 50)
    
    # Clear existing videos (optional - for clean testing)
    result = videos_collection.delete_many({})
    print(f"Cleared {result.deleted_count} existing videos")
    
    # Video 1: Y Combinator - How to Start a Startup
    video1 = {
        'title': 'How to Start a Startup',
        'description': 'Learn the fundamentals of building a successful startup from Y Combinator',
        'youtube_id': 'CBYhVcO4WgI',  # Real YouTube video
        'thumbnail_url': 'https://i.ytimg.com/vi/CBYhVcO4WgI/hqdefault.jpg',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    
    # Video 2: Steve Jobs - Stanford Commencement Speech
    video2 = {
        'title': 'Steve Jobs Stanford Commencement Speech',
        'description': 'Inspirational speech about connecting the dots and following your passion',
        'youtube_id': 'UF8uR6Z6KLc',  # Real YouTube video
        'thumbnail_url': 'https://i.ytimg.com/vi/UF8uR6Z6KLc/hqdefault.jpg',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    
    # Insert videos
    videos_collection.insert_one(video1)
    print(f"✅ Added: {video1['title']}")
    
    videos_collection.insert_one(video2)
    print(f"✅ Added: {video2['title']}")
    
    print("=" * 50)
    print("✅ Database seeded successfully!")
    print("=" * 50)
    
    # Verify by counting
    count = videos_collection.count_documents({'is_active': True})
    print(f"Total active videos: {count}")

if __name__ == '__main__':
    seed_videos()