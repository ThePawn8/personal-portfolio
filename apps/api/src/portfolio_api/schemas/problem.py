"""RFC 9457 problem details — the single shape of every error this API returns."""

from pydantic import BaseModel, ConfigDict, Field


class Problem(BaseModel):
    """An error response (`application/problem+json`).

    Declared as a real schema so the OpenAPI contract documents what clients must handle,
    rather than leaving them to discover the shape from a failing request.

    The wire format is camelCase throughout, so the field carries an alias rather than
    exposing Python naming to the client.
    """

    model_config = ConfigDict(populate_by_name=True)

    type: str = Field(
        description="Stable URI identifying the error kind. Dereference it for guidance.",
        examples=[
            "https://github.com/ThePawn8/personal-portfolio/blob/main/docs/ERRORS.md#not-found"
        ],
    )
    title: str = Field(description="Short, human-readable summary.", examples=["Not found"])
    status: int = Field(description="HTTP status code.", examples=[404])
    detail: str = Field(
        description="Explanation specific to this occurrence.",
        examples=["No published project exists with slug 'unknown'."],
    )
    instance: str = Field(description="Path that produced the error.", examples=["/api/v1/x"])
    request_id: str = Field(
        alias="requestId",
        description="Correlates with the server log line for this request.",
        examples=["01JC4Z8K7Q3M9XKQ0F8W2E5T1V"],
    )
