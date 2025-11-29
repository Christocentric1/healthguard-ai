"""Authentication endpoints for user registration and login"""
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timedelta
from typing import Optional
import uuid

from ..models.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from ..utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from ..database import get_database
from ..config import get_settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Register a new user account

    Creates a new user with hashed password and returns JWT token.

    **Required fields:**
    - email: Valid email address
    - password: Minimum 8 characters
    - full_name: User's full name
    - organisation_id: Organisation identifier
    - role: User role (admin, user, analyst)

    **Returns:**
    - access_token: JWT token for authentication
    - user: User profile information
    """
    db = get_database()

    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user document
    user_id = f"user_{uuid.uuid4().hex[:12]}"
    hashed_password = get_password_hash(user_data.password)

    user_document = {
        "user_id": user_id,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "organisation_id": user_data.organisation_id,
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert user into database
    await db.users.insert_one(user_document)

    # Create indexes for users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index([("organisation_id", 1), ("email", 1)])

    # Generate JWT token
    token_data = {
        "sub": user_id,
        "email": user_data.email,
        "organisation_id": user_data.organisation_id,
        "role": user_data.role
    }
    access_token = create_access_token(token_data)

    # Prepare response
    user_response = UserResponse(
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        organisation_id=user_data.organisation_id,
        role=user_data.role,
        created_at=user_document["created_at"],
        is_active=True
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    """
    Login with email and password

    Authenticates user and returns JWT token.

    **Required fields:**
    - email: User's email address
    - password: User's password

    **Returns:**
    - access_token: JWT token for authentication
    - user: User profile information
    """
    db = get_database()

    # Find user by email
    user = await db.users.find_one({"email": credentials.email.lower()})

    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Generate JWT token
    token_data = {
        "sub": user["user_id"],
        "email": user["email"],
        "organisation_id": user["organisation_id"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)

    # Prepare response
    user_response = UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        full_name=user["full_name"],
        organisation_id=user["organisation_id"],
        role=user["role"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information

    Requires valid JWT token in Authorization header.

    **Headers:**
    - Authorization: Bearer <token>

    **Returns:**
    - User profile information
    """
    db = get_database()

    # Fetch full user details from database
    user = await db.users.find_one({"user_id": current_user["user_id"]})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        full_name=user["full_name"],
        organisation_id=user["organisation_id"],
        role=user["role"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )


@router.post("/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """
    Logout current user

    Note: Since we're using stateless JWT tokens, logout is handled client-side
    by discarding the token. This endpoint exists for consistency and future
    token blacklisting implementation.

    **Headers:**
    - Authorization: Bearer <token>

    **Returns:**
    - Success message
    """
    return {
        "success": True,
        "message": "Successfully logged out. Please discard your token."
    }
