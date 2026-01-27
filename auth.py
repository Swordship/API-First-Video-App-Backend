from flask import Blueprint, request, jsonify
from models import User
from utils import hash_password, verify_password, generate_jwt, token_required
import re

# Create Blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength (min 6 characters)"""
    return len(password) >= 6

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user
    
    Expected JSON:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "password123"
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Check if all fields are present
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user_id = User.create(name, email, password_hash)
        
        # Return success response
        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(user_id)
        }), 201
        
    except Exception as e:
        print(f"Signup error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    
    Expected JSON:
    {
        "email": "john@example.com",
        "password": "password123"
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate required fields
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Find user by email
        user = User.find_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        token = generate_jwt(user['_id'])
        
        # Return token and user info
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_profile(user_id):
    """
    Get current user profile (protected route)
    
    Requires Authorization header: Bearer <token>
    """
    try:
        # Find user by ID (user_id comes from token_required decorator)
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Return user profile (exclude password_hash)
        return jsonify({
            'user': {
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat()
            }
        }), 200
        
    except Exception as e:
        print(f"Get profile error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(user_id):
    """
    Logout user (mock implementation)
    
    In a real app, you'd invalidate the token in a blacklist or database.
    For this assignment, we'll just return success - client clears the token.
    
    Requires Authorization header: Bearer <token>
    """
    try:
        # Mock logout - in production, you'd:
        # 1. Add token to blacklist in Redis
        # 2. Or store token expiry in database
        # 3. Or use refresh tokens and invalidate them
        
        return jsonify({
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        print(f"Logout error: {str(e)}")  # Debug logging
        return jsonify({'error': 'Internal server error'}), 500