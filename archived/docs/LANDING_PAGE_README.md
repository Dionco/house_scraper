# House Scraper Landing Page & Authentication

This update adds a complete authentication flow to the House Scraper application with a beautiful landing page.

## Features Added

### 1. Landing Page (`/`)
- **Beautiful hero section** with call-to-action buttons
- **Feature highlights** showcasing the app's capabilities
- **Authentication modal** for login/register
- **Profile settings modal** for user preferences
- **Responsive design** with modern UI/UX

### 2. Authentication Flow
- **User registration** with username, email, and password
- **User login** with username/email and password
- **JWT token management** with automatic refresh
- **Profile settings** with email notifications and scraping intervals
- **Secure logout** with token blacklisting

### 3. Dashboard Protection
- **Protected routes** - Dashboard only accessible after login
- **Seamless redirect** - Landing page → Dashboard after authentication
- **Session persistence** - Users stay logged in across browser sessions

## File Structure

```
backend/
├── index.html          # New landing page
├── listings.html       # Protected dashboard (existing)
├── auth.js            # Authentication manager (updated)
├── auth_models.py     # Pydantic models (updated)
├── auth_utils.py      # Authentication utilities (existing)
├── api.py             # FastAPI backend (updated)
└── ...
```

## New API Endpoints

### User Profile Management
- `PUT /api/auth/profile` - Update user profile settings
- `GET /api/auth/me` - Get current user info

### Route Structure
- `/` - Landing page (public)
- `/dashboard` - Protected dashboard
- `/api/*` - API endpoints

## User Profile Settings

Users can now configure:
- **Email notifications** for new listings
- **Daily summary emails** 
- **Scraping intervals** (30 minutes to 24 hours)
- **Email address** for notifications

## Authentication Features

### Security
- **JWT tokens** with access/refresh token pattern
- **Password hashing** with bcrypt
- **Token blacklisting** for secure logout
- **Automatic token refresh** to maintain sessions

### User Experience
- **Persistent login** across browser sessions
- **Smooth modal transitions** for auth flows
- **Loading states** for better UX
- **Error handling** with user-friendly messages

## Usage

1. **First Visit**: Users see the landing page with hero section
2. **Registration**: Click "Get Started" to create account
3. **Login**: Click "Sign In" to access existing account
4. **Dashboard**: Automatically redirected to dashboard after auth
5. **Profile**: Click "Profile" to update settings
6. **Logout**: Click "Logout" to end session

## Technical Details

### Authentication Flow
1. User submits credentials
2. Backend validates and issues JWT tokens
3. Frontend stores tokens securely
4. API requests include Authorization header
5. Tokens refresh automatically before expiry

### Profile Settings
- Stored in user record in database
- Updated via dedicated API endpoint
- Synced across all user sessions

### UI Components
- **Landing Page**: Modern hero section with features
- **Auth Modal**: Login/register with form validation
- **Profile Modal**: Settings with form controls
- **Dashboard**: Protected iframe with full functionality

## Development

The landing page is fully self-contained and includes:
- Tailwind CSS for styling
- Vanilla JavaScript for interactivity
- Authentication manager integration
- Responsive design for all devices

## Migration Notes

Existing users can:
- Continue using the application normally
- Access their existing profiles and data
- Update their profile settings via the new interface
- Benefit from the improved authentication system

The dashboard remains fully functional while now being properly protected by authentication.
