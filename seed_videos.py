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
    
    # FIXED: Using open-source videos that ALWAYS allow embedding
    # These videos are specifically made for testing and will work in WebView
    
    # Video 1: Big Buck Bunny (Open source, always works)
    video1 = {
        'title': 'Big Buck Bunny',
        'description': 'Open source animated short film',
        'youtube_id': 'aqz-KE-bpKQ',  # Known to work in embeds
        'thumbnail_url': 'https://i.ytimg.com/vi/aqz-KE-bpKQ/hqdefault.jpg',
        'is_active': True,
        'created_at': datetime.utcnow()
    }
    
    # Video 2: Sintel (Open source, always works)
    video2 = {
        'title': 'Sintel',
        'description': 'Open source animated short film',
        'youtube_id': 'eRsGyueVLvQ',  # Known to work in embeds
        'thumbnail_url': 'https://i.ytimg.com/vi/eRsGyueVLvQ/hqdefault.jpg',
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