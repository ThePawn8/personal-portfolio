"""Profile rules."""

from portfolio_api.core.errors import ProfileNotFoundError
from portfolio_api.repositories.profile import ProfileRepository
from portfolio_api.schemas.profile import ProfileResponse


class ProfileService:
    def __init__(self, repository: ProfileRepository) -> None:
        self._repository = repository

    async def get_profile(self) -> ProfileResponse:
        """The profile, ordered for reading, or a clear 404.

        A missing profile means the seed never ran — a deployment failure, not an empty
        state. Returning an empty object would hide that behind a page that renders blank.
        """
        profile = await self._repository.get()
        if profile is None:
            raise ProfileNotFoundError

        response = ProfileResponse.from_document(profile)

        # Newest first, applied here rather than trusting the file's order: a CV that opens
        # with a job from 2014 reads as a mistake, and an author reordering `profile.yml`
        # should not be able to invert the timeline by accident. `YYYY-MM` strings sort
        # correctly as text, which is why the format was chosen.
        response.experience.sort(key=lambda entry: entry.start, reverse=True)
        response.education.sort(key=lambda entry: entry.end, reverse=True)

        return response
