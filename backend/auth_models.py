"""
Pydantic models for authentication and user management.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserRegister(BaseModel):
    """User registration request model."""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str

class UserResponse(BaseModel):
    """User response model (without sensitive data)."""
    id: str
    username: str
    email: str
    created_at: float
    last_login: Optional[float] = None
    is_active: bool
    profile_ids: List[str] = []

class UserUpdate(BaseModel):
    """User update request model."""
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('Password must contain at least one letter')
            if not re.search(r'[0-9]', v):
                raise ValueError('Password must contain at least one number')
        return v

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class TokenRefresh(BaseModel):
    """Token refresh request model."""
    refresh_token: str

class PasswordReset(BaseModel):
    """Password reset request model."""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('Password must contain at least one letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

class ProfileCreate(BaseModel):
    """Profile creation request model (updated for user context)."""
    name: str = Field(..., min_length=1, max_length=100)
    filters: dict
    emails: List[EmailStr] = []
    scrape_interval_hours: int = Field(default=4, ge=1, le=168)  # 1 hour to 1 week

class ProfileUpdate(BaseModel):
    """Profile update request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    filters: Optional[dict] = None
    emails: Optional[List[EmailStr]] = None
    scrape_interval_hours: Optional[int] = Field(None, ge=1, le=168)

class ProfileResponse(BaseModel):
    """Profile response model."""
    id: str
    user_id: str
    name: str
    filters: dict
    emails: List[str]
    scrape_interval_hours: int
    created_at: float
    last_scraped: Optional[float] = None
    last_new_listings_count: int = 0
    listings_count: int = 0  # Computed field for number of listings
    new_today_count: int = 0  # Computed field for listings added in last 24 hours

class EmailUpdate(BaseModel):
    """Email update request model."""
    emails: List[EmailStr]

class ScrapeIntervalUpdate(BaseModel):
    """Scrape interval update request model."""
    scrape_interval_hours: int = Field(..., ge=1, le=168)
