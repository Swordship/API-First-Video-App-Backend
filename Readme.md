# 🎥 Video Streaming App - Backend API

A secure, scalable REST API built with Flask and MongoDB that powers a video streaming mobile application. Features JWT authentication, dual-token security system, and YouTube video abstraction.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
  - [Manual Setup](#manual-setup)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Security](#security)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Design Decisions](#design-decisions)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This backend API serves as the core of a video streaming application, implementing:

- **API-First Architecture**: Frontend is a thin client with zero business logic
- **Secure Authentication**: JWT-based authentication with bcrypt password hashing
- **Dual-Token System**: Separate tokens for authentication and video access
- **YouTube Abstraction**: Raw video IDs never exposed to frontend
- **Scalable Design**: Built to support multiple clients (mobile, web, desktop)

**Key Design Principle**: All business logic, validation, and data control resides in the backend. The frontend only renders data and makes API calls.

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MOBILE CLIENT (React Native)              │
│  - UI Rendering                                             │
│  - API Calls                                                │
│  - JWT Storage (AsyncStorage)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │ Authorization: Bearer <JWT>
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    FLASK API SERVER                          │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  API Layer (Blueprints)                               │ │
│  │  - /auth/* (Authentication endpoints)                 │ │
│  │  - /video/* (Video endpoints)                         │ │
│  │  - / (Health check)                                   │ │
│  └────────────────────┬──────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼──────────────────────────────────┐ │
│  │  Middleware Layer                                     │ │
│  │  - @token_required (JWT verification)                │ │
│  │  - CORS handling                                     │ │
│  │  - Error handling                                    │ │
│  └────────────────────┬──────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼──────────────────────────────────┐ │
│  │  Business Logic Layer                                │ │
│  │  - User validation                                   │ │
│  │  - Password hashing (bcrypt)                         │ │
│  │  - JWT generation/verification                       │ │
│  │  - Playback token generation                         │ │
│  │  - Video filtering                                   │ │
│  │  - YouTube URL abstraction                           │ │
│  └────────────────────┬──────────────────────────────────┘ │
└────────────────────────┼────────────────────────────────────┘
                         │
                         │ PyMongo
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    MONGODB DATABASE                          │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Collections:                                         │ │
│  │  - users (authentication, profiles)                   │ │
│  │  - videos (metadata, youtube_ids)                     │ │
│  │                                                        │ │
│  │  Indexes:                                             │ │
│  │  - users.email (unique)                               │ │
│  │  - videos.is_active                                   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Videos stored here,
                         │ streamed from:
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    YOUTUBE                                   │
│  - Videos: Y Combinator lectures, Steve Jobs speech         │
│  - Frontend never sees raw youtube_id                       │
│  - Backend returns youtube-nocookie.com embed URLs          │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Diagrams

#### User Authentication Flow

```
1. User Signup
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │  Client  │────────▶│  Flask   │────────▶│ MongoDB  │
   └──────────┘         └──────────┘         └──────────┘
   
   POST /auth/signup
   {
     name, email, password
   }
   
   ──────────────────────────────────────────────────────
   
   Validation:
   ├─ Email format check
   ├─ Password length ≥ 6
   ├─ Check if email exists
   └─ Hash password (bcrypt)
   
   ──────────────────────────────────────────────────────
   
   Response:
   {
     message: "User registered successfully",
     user_id: "..."
   }

2. User Login
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │  Client  │────────▶│  Flask   │────────▶│ MongoDB  │
   └──────────┘         └──────────┘         └──────────┘
   
   POST /auth/login
   {
     email, password
   }
   
   ──────────────────────────────────────────────────────
   
   Validation:
   ├─ Find user by email
   ├─ Verify password (bcrypt)
   └─ Generate JWT (24h expiry)
   
   ──────────────────────────────────────────────────────
   
   Response:
   {
     token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     user: {id, name, email}
   }
```

#### Video Streaming Flow

```
1. Dashboard Request
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │  Client  │────────▶│  Flask   │────────▶│ MongoDB  │
   └──────────┘         └──────────┘         └──────────┘
   
   GET /dashboard
   Headers: Authorization: Bearer <JWT>
   
   ──────────────────────────────────────────────────────
   
   Processing:
   ├─ Verify JWT (@token_required)
   ├─ Query: videos.find({is_active: true}).limit(2)
   ├─ For each video:
   │  └─ Generate playback_token (1h expiry, video-specific)
   └─ Return video metadata + playback_tokens
   
   ──────────────────────────────────────────────────────
   
   Response:
   {
     videos: [
       {
         id, title, description, thumbnail_url,
         playback_token: "eyJ..."
       }
     ]
   }

2. Video Stream Request
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │  Client  │────────▶│  Flask   │────────▶│ MongoDB  │
   └──────────┘         └──────────┘         └──────────┘
   
   GET /video/{id}/stream?token={playback_token}
   Headers: Authorization: Bearer <JWT>
   
   ──────────────────────────────────────────────────────
   
   Security Checks:
   ├─ Verify JWT (user authentication)
   ├─ Verify playback_token (video access)
   ├─ Match video_id in URL with token
   ├─ Check video.is_active == true
   └─ Abstract youtube_id to embed URL
   
   ──────────────────────────────────────────────────────
   
   Response:
   {
     stream_url: "https://youtube-nocookie.com/embed/{id}?...",
     video_id: "...",
     title: "..."
   }
```

---

## 🛠️ Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Backend language |
| **Flask** | 3.0.0 | Web framework |
| **MongoDB** | 7.0 | NoSQL database |
| **PyMongo** | 4.9.1 | MongoDB driver |
| **PyJWT** | 2.8.0 | JWT tokens |
| **Bcrypt** | 4.1.2 | Password hashing |
| **Flask-CORS** | 4.0.0 | CORS handling |
| **Docker** | - | Containerization |

### Why These Technologies?

**Flask:**
- Lightweight and flexible
- Easy to structure with Blueprints
- Perfect for REST APIs
- Fast development cycle

**MongoDB:**
- Flexible schema for rapid iteration
- Natural fit for document-based data
- Easy to work with in Python
- Scales horizontally

**JWT:**
- Stateless authentication
- Self-contained tokens
- No server-side session storage
- Easy to scale across multiple servers

**Bcrypt:**
- Industry-standard password hashing
- Automatic salting
- Adjustable work factor
- Resistant to rainbow table attacks

---

## ✨ Features

### Authentication & Security

- ✅ **JWT Authentication**: Secure token-based authentication with 24-hour expiry
- ✅ **Password Security**: Bcrypt hashing with automatic salting
- ✅ **Dual-Token System**: 
  - Auth JWT: Proves user identity (24 hours)
  - Playback Token: Controls video access (1 hour, video-specific)
- ✅ **Input Validation**: Server-side validation for all inputs
- ✅ **CORS Configuration**: Controlled access for React Native clients

### Video Management

- ✅ **YouTube Abstraction**: Raw video IDs never exposed to frontend
- ✅ **Active Video Filtering**: Only active videos returned to clients
- ✅ **Playback Token Generation**: Short-lived tokens for video access
- ✅ **Scalable Video Source**: Easy to switch from YouTube to custom CDN

### API Design

- ✅ **RESTful Architecture**: Standard HTTP methods and status codes
- ✅ **Blueprint Organization**: Modular code structure
- ✅ **Comprehensive Error Handling**: Proper error messages and status codes
- ✅ **Health Check Endpoint**: Monitor API status

### Database

- ✅ **Indexed Collections**: Fast queries with proper indexes
- ✅ **Data Validation**: MongoDB schema validation
- ✅ **Automatic Timestamps**: Created_at for all documents

---

## 🚀 Getting Started

### Prerequisites

**Required:**
- Docker Desktop (recommended) OR
- Python 3.11+
- MongoDB 7.0+

**Optional:**
- MongoDB Compass (for database visualization)
- Postman (for API testing)

---

### Docker Setup (Recommended)

Docker provides the easiest and most consistent way to run the backend.

**1. Install Docker Desktop**

Download and install from: https://www.docker.com/products/docker-desktop

**2. Clone the repository**

```bash
git clone <your-backend-repo-url>
cd backend-repo
```

**3. Start the application**

```bash
docker-compose up -d
```

**What this does:**
- Downloads MongoDB 7.0 image
- Builds Flask backend image
- Starts MongoDB container
- Starts Flask backend container
- Automatically seeds database with 2 videos
- Exposes API on http://localhost:5000

**4. Verify it's running**

```bash
# Check container status
docker-compose ps

# Expected output:
# NAME                  STATUS              PORTS
# video-app-backend     Up (healthy)        0.0.0.0:5000->5000/tcp
# video-app-mongodb     Up (healthy)        0.0.0.0:27017->27017/tcp

# Test API
curl http://localhost:5000/
```

**5. View logs**

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend
```

**6. Stop the application**

```bash
docker-compose down
```

For detailed Docker instructions, see [DOCKER.md](./DOCKER.md)

---

### Manual Setup

If you prefer to run without Docker:

**1. Create virtual environment**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Set up environment variables**

```bash
# Copy example file
cp .env.example .env

# Edit .env with your values:
# MONGODB_URI=mongodb://localhost:27017/video_app
# JWT_SECRET_KEY=your_super_secret_key
# FLASK_ENV=development
```

**4. Start MongoDB**

```bash
# Make sure MongoDB is running
mongod --version

# If not installed, download from:
# https://www.mongodb.com/try/download/community
```

**5. Seed database**

```bash
python seed_videos.py
```

**6. Run the application**

```bash
python app.py
```

API will be available at http://localhost:5000

---

## 📡 API Documentation

### Base URL

```
Local: http://localhost:5000
Network: http://<your-ip>:5000
```

### Authentication

All protected endpoints require JWT token in header:

```
Authorization: Bearer <your_jwt_token>
```

---

### Endpoints

#### Health Check

```http
GET /
```

**Response:**
```json
{
  "message": "Video App API",
  "status": "running",
  "version": "1.0.0"
}
```

---

#### User Signup

```http
POST /auth/signup
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

**Validation:**
- Name: Required, non-empty string
- Email: Required, valid email format
- Password: Required, minimum 6 characters

**Success Response (201):**
```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

**Error Responses:**
- 400: Missing or invalid fields
- 409: Email already registered

---

#### User Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

**Success Response (200):**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Error Responses:**
- 400: Missing fields
- 401: Invalid email or password

---

#### Get User Profile

```http
GET /auth/me
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2026-01-28T10:30:00"
  }
}
```

**Error Responses:**
- 401: Token missing, invalid, or expired
- 404: User not found

---

#### Logout

```http
POST /auth/logout
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "message": "Logout successful"
}
```

**Note:** This is a mock implementation. In production, you would:
- Add token to blacklist in Redis
- Invalidate refresh tokens
- Clear server-side sessions

---

#### Get Dashboard Videos

```http
GET /dashboard
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "videos": [
    {
      "id": "507f1f77bcf86cd799439012",
      "title": "How to Start a Startup - Sam Altman (Y Combinator)",
      "description": "Learn the fundamentals of building a successful startup...",
      "thumbnail_url": "https://i.ytimg.com/vi/CBYhVcO4WgI/hqdefault.jpg",
      "playback_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    },
    {
      "id": "507f1f77bcf86cd799439013",
      "title": "Steve Jobs Stanford Commencement Address",
      "description": "Steve Jobs delivers an inspiring commencement speech...",
      "thumbnail_url": "https://i.ytimg.com/vi/UF8uR6Z6KLc/hqdefault.jpg",
      "playback_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
  ]
}
```

**Features:**
- Returns exactly 2 active videos
- Each video includes a playback_token (1 hour expiry)
- Tokens are video-specific

---

#### Get Video Stream URL

```http
GET /video/{video_id}/stream?token={playback_token}
Authorization: Bearer <jwt_token>
```

**Parameters:**
- `video_id`: MongoDB ObjectId of the video
- `token`: Playback token from dashboard response

**Success Response (200):**
```json
{
  "stream_url": "https://www.youtube-nocookie.com/embed/CBYhVcO4WgI?autoplay=0&controls=1&playsinline=1&enablejsapi=1",
  "video_id": "507f1f77bcf86cd799439012",
  "title": "How to Start a Startup - Sam Altman (Y Combinator)"
}
```

**Security Checks:**
1. Verify auth JWT (user authentication)
2. Verify playback token (video access)
3. Match video_id in URL with token
4. Check video is active
5. Return abstracted YouTube URL

**Error Responses:**
- 400: Playback token missing
- 401: Invalid or expired playback token
- 403: Video ID mismatch or video inactive
- 404: Video not found

---

## 🗄️ Database Schema

### Users Collection

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  name: "John Doe",
  email: "john@example.com",        // Unique, indexed, lowercase
  password_hash: "$2b$12$...",       // Bcrypt hash
  created_at: ISODate("2026-01-28T10:30:00Z")
}
```

**Indexes:**
- `email` (unique): Fast lookup, duplicate prevention

---

### Videos Collection

```javascript
{
  _id: ObjectId("507f1f77bcf86cd799439012"),
  title: "How to Start a Startup - Sam Altman (Y Combinator)",
  description: "Learn the fundamentals of building a successful startup...",
  youtube_id: "CBYhVcO4WgI",        // NEVER exposed to frontend
  thumbnail_url: "https://i.ytimg.com/vi/CBYhVcO4WgI/hqdefault.jpg",
  is_active: true,                   // Indexed for fast filtering
  created_at: ISODate("2026-01-28T10:30:00Z")
}
```

**Indexes:**
- `is_active`: Fast filtering of active videos

---

## 🔐 Security

### Authentication Flow

**1. User Signup:**
```
Password → Bcrypt Hash (with salt) → Store in MongoDB
```

**2. User Login:**
```
Password → Bcrypt Verify → Generate JWT (24h) → Return to client
```

**3. Protected Routes:**
```
Request → Extract JWT → Verify Signature → Verify Expiry → Allow Access
```

### Dual-Token System

**Why Two Tokens?**

**Auth JWT (24 hours):**
- Proves user identity
- Required for all protected endpoints
- Long-lived for good UX

**Playback Token (1 hour):**
- Controls access to specific videos
- Short-lived for security
- Video-specific (can't be reused for other videos)

**Benefits:**
- Fine-grained access control
- Can implement premium videos
- Can track video views
- Can implement time-limited access
- Prevents token reuse for unauthorized videos

### YouTube Abstraction

**Why Abstract YouTube?**

1. **Security**: Raw video IDs never exposed to frontend
2. **Flexibility**: Easy to switch video sources (Vimeo, custom CDN)
3. **Control**: Backend decides which videos are available
4. **Analytics**: Can track video access
5. **Future-proof**: Can implement CDN, transcoding, DRM

**Implementation:**
```
Frontend Request → Backend verifies access → Backend returns embed URL
Frontend extracts ID → YouTube iFrame player plays video
```

### Security Best Practices

- ✅ Passwords hashed with bcrypt (salted, work factor 12)
- ✅ JWT with HS256 algorithm
- ✅ Tokens expire (24h auth, 1h playback)
- ✅ Email stored as lowercase (prevents bypassing)
- ✅ Server-side validation for all inputs
- ✅ CORS configured for specific origins
- ✅ Error messages don't leak sensitive info
- ✅ MongoDB injection prevented (PyMongo parameterization)

---

## 🧪 Testing

### Manual Testing with cURL

**1. Test health check:**
```bash
curl http://localhost:5000/
```

**2. Test signup:**
```bash
curl -X POST http://localhost:5000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"test123"}'
```

**3. Test login:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'
```

**4. Test dashboard (with token):**
```bash
curl -X GET http://localhost:5000/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Testing with Postman

1. Import the API endpoints
2. Create environment variable for JWT token
3. Test each endpoint in sequence
4. Verify responses match documentation

### Automated Testing

```bash
# Run tests (if implemented)
pytest

# Run with coverage
pytest --cov=.
```

---

## 📁 Project Structure

```
backend-repo/
│
├── app.py                  # Flask application entry point
│   ├── Creates Flask app
│   ├── Loads configuration
│   ├── Registers blueprints
│   ├── Sets up CORS
│   └── Defines error handlers
│
├── config.py               # Configuration management
│   ├── Environment variables
│   ├── MongoDB URI
│   ├── JWT settings
│   └── Flask environment
│
├── models.py               # Database models
│   ├── User model (CRUD operations)
│   ├── Video model (CRUD operations)
│   ├── Database connection
│   └── Index creation
│
├── auth.py                 # Authentication blueprint
│   ├── POST /auth/signup
│   ├── POST /auth/login
│   ├── GET /auth/me
│   └── POST /auth/logout
│
├── video.py                # Video blueprint
│   ├── GET /dashboard
│   ├── GET /video/<id>/stream
│   ├── generate_playback_token()
│   └── verify_playback_token()
│
├── utils.py                # Utility functions
│   ├── hash_password()
│   ├── verify_password()
│   ├── generate_jwt()
│   ├── verify_jwt()
│   └── @token_required decorator
│
├── seed_videos.py          # Database seeding
│   └── Populates videos collection
│
├── requirements.txt        # Python dependencies
│
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
│
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker orchestration
├── .dockerignore           # Docker ignore rules
│
└── README.md               # This file
```

---

## 🎯 Design Decisions

### 1. API-First Architecture

**Decision:** All business logic in backend, frontend is thin client.

**Why:**
- **Scalability**: Can serve multiple clients (mobile, web, desktop)
- **Security**: Validation and logic on trusted server
- **Maintainability**: Changes in one place
- **Flexibility**: Can replace frontend without changing backend

**Trade-offs:**
- More API calls (but acceptable with good network)
- Slightly more latency (but negligible)

---

### 2. Dual-Token System

**Decision:** Separate tokens for authentication and video access.

**Why:**
- **Fine-grained control**: Can control video access independently
- **Security**: Short-lived playback tokens reduce risk
- **Flexibility**: Can implement premium videos, time-limited access
- **Analytics**: Can track which videos are accessed

**Trade-offs:**
- More complex (but well-documented)
- Extra token generation (but fast)

---

### 3. YouTube Abstraction

**Decision:** Backend hides raw YouTube IDs from frontend.

**Why:**
- **Security**: IDs not exposed in client code
- **Flexibility**: Easy to switch video sources
- **Control**: Backend decides available videos
- **Future-proof**: Can add CDN, transcoding, DRM

**Trade-offs:**
- Extra API call for stream URL (but cached)

---

### 4. MongoDB over SQL

**Decision:** NoSQL database for this project.

**Why:**
- **Flexible schema**: Easy to iterate quickly
- **Document model**: Natural fit for users and videos
- **Scalability**: Horizontal scaling
- **Python integration**: Easy with PyMongo

**When SQL is better:**
- Complex relationships
- ACID transactions required
- Complex queries with JOINs

---

### 5. JWT over Sessions

**Decision:** Stateless authentication with JWT.

**Why:**
- **Stateless**: No server-side session storage
- **Scalable**: Works across multiple servers
- **Mobile-friendly**: Easy to store on mobile devices
- **Self-contained**: All info in token

**Trade-offs:**
- Can't invalidate tokens (solved with short expiry)
- Tokens can grow large (but acceptable for our use case)

---

### 6. Bcrypt for Password Hashing

**Decision:** Bcrypt over other hashing algorithms.

**Why:**
- **Industry standard**: Battle-tested
- **Automatic salting**: No manual salt management
- **Adjustable work factor**: Can increase security over time
- **Rainbow table resistant**: Salting prevents pre-computed attacks

---

## 🐛 Troubleshooting

### MongoDB Connection Error

**Problem:**
```
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions:**

1. **Docker setup:**
```bash
# Check if MongoDB container is running
docker-compose ps

# Check MongoDB logs
docker-compose logs mongodb

# Restart services
docker-compose restart
```

2. **Manual setup:**
```bash
# Check if MongoDB is running
mongod --version

# Start MongoDB
mongod

# Check connection string in .env
MONGODB_URI=mongodb://localhost:27017/video_app
```

---

### JWT Token Invalid

**Problem:**
```json
{"error": "Token is invalid or expired"}
```

**Solutions:**

1. **Token expired**: Token has 24-hour expiry, login again

2. **Wrong secret key**:
```bash
# Ensure JWT_SECRET_KEY is consistent
# Check .env file
```

3. **Header format**:
```bash
# Correct format:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Wrong format:
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solutions:**

1. **Activate virtual environment**:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Docker setup**:
```bash
# Rebuild image
docker-compose up -d --build backend
```

---

### Port Already in Use

**Problem:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. **Find and kill process**:
```bash
# Mac/Linux
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

2. **Change port** in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

### Database Empty After Restart

**Problem:** No videos showing in dashboard.

**Solutions:**

1. **Re-seed database**:
```bash
# Docker
docker-compose exec backend python seed_videos.py

# Manual
python seed_videos.py
```

2. **Check database**:
```bash
# Docker
docker-compose exec mongodb mongosh video_app

# Manual
mongosh video_app

# Then run:
db.videos.countDocuments()
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyMongo Tutorial](https://pymongo.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT debugger
- [MongoDB Manual](https://docs.mongodb.com/)
- [Bcrypt Documentation](https://github.com/pyca/bcrypt/)
- [Docker Documentation](https://docs.docker.com/)

---

## 🤝 Contributing

This project was built as a technical assignment to demonstrate:
- Full-stack development skills
- API design
- Security best practices
- System architecture
- Docker deployment
- Production-ready code

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 👤 Author

**Your Name**
- GitHub: [Swordship](https://github.com/Swordship)
- LinkedIn: [Monish S](https://www.linkedin.com/in/monish-s-a37482274)

---

## 🎯 Assignment Checklist

This backend was built to meet all assignment requirements:

- ✅ Flask REST API
- ✅ MongoDB database
- ✅ JWT authentication (signup, login, profile, logout)
- ✅ User model with password hashing
- ✅ Video model with YouTube abstraction
- ✅ Dashboard endpoint (returns 2 videos)
- ✅ Video stream endpoint with dual tokens
- ✅ API-first architecture
- ✅ Comprehensive error handling
- ✅ Clean code structure with blueprints
- ✅ **BONUS: Docker deployment**

---

**Backend is production-ready and thoroughly documented!** 🚀