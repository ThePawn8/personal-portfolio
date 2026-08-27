"""Profile endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from portfolio_api.core.http_cache import cached_json_response
from portfolio_api.repositories.profile import ProfileRepository
from portfolio_api.schemas.profile import ProfileResponse
from portfolio_api.services.profile import ProfileService

router = APIRouter(prefix="/api/v1", tags=["profile"])


def get_profile_service() -> ProfileService:
    return ProfileService(ProfileRepository())


ProfileServiceDep = Annotated[ProfileService, Depends(get_profile_service)]


@router.get(
    "/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the author profile",
    response_description="Bio, experience, education, skills and links.",
)
async def get_profile(request: Request, service: ProfileServiceDep) -> Response:
    profile = await service.get_profile()

    return cached_json_response(request, profile.model_dump(by_alias=True))
