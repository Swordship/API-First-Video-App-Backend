from flask import Blueprint, request, jsonify
from models import Video
from utils import token_required, generate_jwt
from bson import ObjectId
import jwt
from config import Config

# Create Blueprint for video routes
video_bp = Blueprint('video', __name__)

@video_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard(user_id):
    """
    Get dashboard videos (limited to 2)
    
    Requires Authorization header: Bearer <token>
    
    Returns:
    {
        "videos": [
            {
                "id": "...",
                "title": "...",
                "description": "...",
                "thumbnail_url": "...",
                "playback_token": "..."
            }
        ]
    }
    """
    try:
        # Get 2 active videos from database
        videos = Video.get_active_videos(limit=2)
        
        # Format response
        video_list = []
        for video in videos:
            # Generate playback token for this video
            # This token will be used to request the stream URL
            playback_token = generate_playback_token(str(video['_id']))
            
            video_list.append({
                'id': str(video['_id']),
                'title': video['title'],
                'description': video['description'],
                'thumbnail_url': video['thumbnail_url'],
                'playback_token': playback_token  # Token to access video stream
            })
        
        return jsonify({
            'videos': video_list
        }), 200
        
    except Exception as e:
        print(f"Dashboard error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Internal server error'}), 500

@video_bp.route('/video/<video_id>/stream', methods=['GET'])
@token_required
def get_video_stream(user_id, video_id):
    """
    Get video stream URL (YouTube abstraction)
    
    Requires:
    - Authorization header: Bearer <token>
    - Query param: ?token=<playback_token>
    
    Returns:
    {
        "stream_url": "https://www.youtube.com/embed/...",
        "video_id": "..."
    }
    """
    try:
        # Get playback token from query params
        playback_token = request.args.get('token')
        
        if not playback_token:
            return jsonify({'error': 'Playback token is required'}), 400
        
        # Verify playback token
        video_id_from_token = verify_playback_token(playback_token)
        if not video_id_from_token:
            return jsonify({'error': 'Invalid or expired playback token'}), 401
        
        # Check if video_id in URL matches token
        if video_id_from_token != video_id:
            return jsonify({'error': 'Video ID mismatch'}), 403
        
        # Get video from database
        video = Video.find_by_id(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        if not video['is_active']:
            return jsonify({'error': 'Video is not available'}), 403
        
        # Generate YouTube embed URL (abstracted from frontend)
        # Frontend NEVER sees the raw youtube_id - only gets embed URL
        youtube_id = video['youtube_id']
        stream_url = f"https://www.youtube.com/embed/{youtube_id}?autoplay=0&controls=1"
        
        return jsonify({
            'stream_url': stream_url,
            'video_id': str(video['_id']),
            'title': video['title']
        }), 200
        
    except Exception as e:
        print(f"Video stream error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Internal server error'}), 500

# Helper functions for playback tokens

def generate_playback_token(video_id):
    """
    Generate a playback token for a specific video
    
    This token is different from auth JWT - it's video-specific
    and short-lived (1 hour)
    """
    from datetime import datetime, timedelta
    
    payload = {
        'video_id': video_id,
        'exp': datetime.utcnow() + timedelta(hours=1),  # Expires in 1 hour
        'iat': datetime.utcnow(),
        'type': 'playback'  # Token type identifier
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token

def verify_playback_token(token):
    """
    Verify playback token and return video_id
    
    Returns video_id if valid, None if invalid/expired
    """
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
        
        # Check token type
        if payload.get('type') != 'playback':
            return None
        
        return payload.get('video_id')
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token