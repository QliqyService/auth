from pydantic import BaseModel, Field


class PerpetualTokenResponse(BaseModel):
    """Response schema for perpetual token generation."""

    access_token: str = Field(..., description="Perpetual access token")
