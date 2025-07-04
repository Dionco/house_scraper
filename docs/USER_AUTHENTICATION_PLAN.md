# User Authentication and Authorization System

## Dependencies Added
```
python-jose[cryptography]  # JWT tokens
passlib[bcrypt]           # Password hashing
python-multipart          # Form data handling
```

## Database Schema Changes

### Users Table Structure
```json
{
  "users": {
    "user_123456": {
      "id": "user_123456",
      "username": "john_doe",
      "email": "john@example.com",
      "password_hash": "$2b$12$...",
      "created_at": 1625097600,
      "last_login": 1625097600,
      "is_active": true,
      "profile_ids": ["profile_1234", "profile_5678"]
    }
  }
}
```

### Updated Profile Structure
```json
{
  "profiles": {
    "profile_1234": {
      "id": "profile_1234",
      "user_id": "user_123456",  // NEW: Link to user
      "name": "Utrecht Search",
      "filters": { ... },
      "emails": [...],
      "listings": [...],
      // ... existing fields
    }
  }
}
```

## API Endpoints

### Authentication Routes
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/me` - Update user profile

### Protected Routes (require authentication)
- `GET /api/profiles` - Get user's profiles only
- `POST /api/profiles` - Create profile for authenticated user
- `PUT /api/profiles/{id}` - Update user's profile only
- `DELETE /api/profiles/{id}` - Delete user's profile only
- `GET /api/listings` - Get listings for user's profiles

## Security Features

### Password Security
- bcrypt hashing with salt rounds
- Password strength validation
- Secure password reset flow

### JWT Token Security
- Access tokens (15 min expiry)
- Refresh tokens (7 days expiry)
- Secure HTTP-only cookies for refresh tokens
- Token blacklisting for logout

### Route Protection
- Authentication middleware
- User ownership validation
- Rate limiting on auth endpoints

## Frontend Changes

### New Components
- LoginForm component
- RegisterForm component
- AuthGuard component
- UserProfile component
- ProtectedRoute wrapper

### State Management
- User authentication state
- JWT token management
- Automatic token refresh
- Logout handling

### UI Updates
- Login/Register modal
- User menu in header
- Profile ownership indicators
- Session timeout notifications

## Implementation Steps

1. **Backend Setup**
   - Install new dependencies
   - Create auth models and utilities
   - Add authentication middleware
   - Create auth endpoints
   - Update existing endpoints

2. **Database Migration**
   - Create migration script
   - Update database schema
   - Link existing profiles to admin user

3. **Frontend Integration**
   - Create auth components
   - Update API client with token handling
   - Add route protection
   - Update UI for user context

4. **Security & Testing**
   - Add environment variables
   - Implement security headers
   - Add comprehensive tests
   - Security audit

## Environment Variables
```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./app.db  # Future SQLite/PostgreSQL migration

# Security
BCRYPT_ROUNDS=12
```
