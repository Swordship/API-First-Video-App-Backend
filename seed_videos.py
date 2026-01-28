from models import videos_collection
from datetime import datetime

def seed_videos():
    """Seed database with 2 startup-focused videos"""
    
    print("=" * 50)
    print("🌱 Seeding database with startup videos...")
    print("=" * 50)
    
    # Clear existing videos (optional - for clean testing)
    result = videos_collection.delete_many({})
    print(f"Cleared {result.deleted_count} existing videos")
    
    # Video 1: Y Combinator - How to Start a Startup
    # This is Sam Altman's famous lecture series at Stanford
    video1 = {
        'title': 'How to Start a Startup - Sam Altman (Y Combinator)',
        'description': 'Learn the fundamentals of building a successful startup from Y Combinator president Sam Altman. Covers ideas, products, teams, and execution strategies used by the world\'s most successful startups.',
        'youtube_id': 'CBYhVcO4WgI',  # Sam Altman's lecture at Stanford
        'thumbnail_url': 'https://i.ytimg.com/vi/CBYhVcO4WgI/hqdefault.jpg',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    
    # Video 2: Steve Jobs - Stanford Commencement Speech
    # Inspirational speech about entrepreneurship and following your passion
    video2 = {
        'title': 'Steve Jobs Stanford Commencement Address',
        'description': 'Steve Jobs delivers an inspiring commencement speech at Stanford University about connecting the dots, love and loss, and living each day as if it were your last. A must-watch for aspiring entrepreneurs.',
        'youtube_id': 'UF8uR6Z6KLc',  # Steve Jobs Stanford speech
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