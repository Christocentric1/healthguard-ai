"""Authentication utilities"""
from fastapi import Header, HTTPException, status


async def get_organisation_id(x_org_id: str = Header(..., description="Organisation ID")) -> str:
    """
    Extract and validate organisation ID from request header.

    Args:
        x_org_id: Organisation ID from X-Org-Id header

    Returns:
        Organisation ID string

    Raises:
        HTTPException: If organisation ID is missing or invalid
    """
    if not x_org_id or x_org_id.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-Org-Id header"
        )
    return x_org_id.strip()
