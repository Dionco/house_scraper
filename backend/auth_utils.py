"""
Authentication utilities for the House Scraper application.
Provides JWT token handling, password hashing, and user management.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer(auto_error=False)

def is_running_on_railway() -> bool:
    """Check if the application is running on Railway."""
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

class AuthUtils:
    """Utility class for authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise AuthenticationError(f"Invalid token type. Expected {token_type}")
            
            # Check expiration
            exp = payload.get("exp")
            if exp is None:
                raise AuthenticationError("Token missing expiration")
            
            if datetime.utcnow() > datetime.fromtimestamp(exp):
                raise AuthenticationError("Token expired")
            
            return payload
            
        except JWTError as e:
            raise AuthenticationError(f"Token validation failed: {str(e)}")
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """
        Validate password strength.
        Requirements: At least 8 characters, containing letters and numbers.
        """
        if len(password) < 8:
            return False
        
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        return has_letter and has_number
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        Validate username format.
        Requirements: 3-30 characters, alphanumeric and underscore only.
        """
        if not username or len(username) < 3 or len(username) > 30:
            return False
        
        return username.replace("_", "").isalnum()

# Global token blacklist (in production, use Redis or database)
token_blacklist = set()

def blacklist_token(token: str):
    """Add token to blacklist."""
    token_blacklist.add(token)

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted."""
    return token in token_blacklist

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user.
    Can be used with @Depends(get_current_user) in route handlers.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = AuthUtils.verify_token(token, "access")
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Load user from database
        # Check if running on Railway (production) or locally
        try:
            if is_running_on_railway():
                from .api import load_db  # Railway (production/deployment) - relative import
            else:
                from api import load_db   # Local development - absolute import
        except ImportError:
            # Fallback: try the other import method
            try:
                if is_running_on_railway():
                    from api import load_db  # Fallback for Railway
                else:
                    from .api import load_db  # Fallback for local
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not import database module"
                )
        db = load_db()
        users = db.get("users", {})
        user = users.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """
    Dependency to get current user if authenticated, or None if not.
    Useful for endpoints that work both with and without authentication.
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None

def create_user_dict(user_id: str, username: str, email: str, password: str) -> Dict[str, Any]:
    """Create a new user dictionary with proper structure."""
    return {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": AuthUtils.hash_password(password),
        "created_at": time.time(),
        "last_login": None,
        "is_active": True,
        "profile_ids": []
    }

def generate_user_id() -> str:
    """Generate a unique user ID."""
    return f"user_{int(time.time())}"

def generate_tokens(user_id: str) -> Dict[str, str]:
    """Generate access and refresh tokens for a user."""
    access_token = AuthUtils.create_access_token(data={"sub": user_id})
    refresh_token = AuthUtils.create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
