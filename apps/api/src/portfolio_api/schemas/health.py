"""Schemas for the health endpoints."""

from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response returned by the liveness probe."""

    status: Literal["ok"] = Field(description="Always `ok` when the process can respond.")
    version: str = Field(description="Deployed application version.", examples=["0.1.0"])
