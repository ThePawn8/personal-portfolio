"""Profile queries."""

from portfolio_api.models import Profile
from portfolio_api.models.profile import PROFILE_KEY


class ProfileRepository:
    async def get(self) -> Profile | None:
        return await Profile.find_one(Profile.key == PROFILE_KEY)
