from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from auth import auth_bp
from video import video_bp

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Enable CORS (allows React Native to make requests)
CORS(app, resources={
    r"/*": {
        "origins": "*",  # In production, specify your app's origin
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(video_bp)

# Root route
@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'message': 'Video App API',
        'status': 'running',
        'version': '1.0.0'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

# Run app
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Video App Backend Starting...")
    print("=" * 50)
    print(f"Environment: {Config.DEBUG and 'Development' or 'Production'}")
    print(f"MongoDB: {Config.MONGODB_URI}")
    print("=" * 50)
    print("Available endpoints:")
    print("  POST   /auth/signup")
    print("  POST   /auth/login")
    print("  GET    /auth/me")
    print("  POST   /auth/logout")
    print("  GET    /dashboard")
    print("  GET    /video/<id>/stream")
    print("=" * 50)
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)