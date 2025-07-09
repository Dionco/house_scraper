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
    email_notifications: Optional[bool] = True
    daily_summaries: Optional[bool] = False
    scrape_interval: Optional[int] = 60  # Default to 60 minutes

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
    scrape_interval_hours: Optional[int] = Field(default=4, ge=0, le=168)
    scrape_interval_minutes: Optional[int] = Field(default=0, ge=0, le=59)  # Minutes component (0-59)
    
    @validator('scrape_interval_minutes')
    def validate_interval(cls, v, values):
        hours = values.get('scrape_interval_hours', 4)
        if hours is None:
            hours = 4
        if v is None:
            v = 0
            
        # Must have at least 1 minute total
        total_minutes = (hours * 60) + v
        if total_minutes < 1:
            raise ValueError('Interval must be at least 1 minute total')
        if total_minutes > 10080:  # 1 week in minutes
            raise ValueError('Interval cannot exceed 1 week')
            
        return v

class ProfileUpdate(BaseModel):
    """Profile update request model."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    filters: Optional[dict] = None
    emails: Optional[List[EmailStr]] = None
    scrape_interval_hours: Optional[int] = Field(None, ge=0, le=168)
    scrape_interval_minutes: Optional[int] = Field(None, ge=0, le=59)  # Minutes component (0-59)
    
    @validator('scrape_interval_minutes')
    def validate_interval(cls, v, values):
        hours = values.get('scrape_interval_hours')
        
        # If both are None, that's fine for partial updates
        if v is None and hours is None:
            return v
        
        # If only one is provided, use default for the other
        if hours is None:
            hours = 0
        if v is None:
            v = 0
            
        # Must have at least 1 minute total
        total_minutes = (hours * 60) + v
        if total_minutes < 1:
            raise ValueError('Interval must be at least 1 minute total')
        if total_minutes > 10080:  # 1 week in minutes
            raise ValueError('Interval cannot exceed 1 week')
            
        return v

class ProfileResponse(BaseModel):
    """Profile response model."""
    id: str
    user_id: str
    name: str
    filters: dict
    emails: List[str]
    scrape_interval_hours: Optional[int] = None
    scrape_interval_minutes: Optional[int] = None
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
    scrape_interval_hours: Optional[int] = Field(None, ge=0, le=168)
    scrape_interval_minutes: Optional[int] = Field(None, ge=0, le=59)  # 0-59 minutes component
    
    @validator('scrape_interval_minutes')
    def validate_interval(cls, v, values):
        hours = values.get('scrape_interval_hours', 0)
        if hours is None:
            hours = 0
        if v is None:
            v = 0
            
        # Must have at least 1 minute total (either from hours or minutes)
        total_minutes = (hours * 60) + v
        if total_minutes < 1:
            raise ValueError('Interval must be at least 1 minute total')
        if total_minutes > 10080:  # 1 week in minutes
            raise ValueError('Interval cannot exceed 1 week')
            
        return v

class UserProfileUpdate(BaseModel):
    """User profile settings update model."""
    email: Optional[EmailStr] = None
    email_notifications: Optional[bool] = None
    daily_summaries: Optional[bool] = None
    scrape_interval: Optional[int] = Field(None, ge=30, le=1440)  # 30 minutes to 24 hours
