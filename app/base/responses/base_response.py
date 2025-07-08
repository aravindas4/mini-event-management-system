from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class BaseResponse(BaseModel, Generic[DataT]):
    """Base class for all response schemas."""

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_domain(cls, domain_model: Any) -> "BaseResponse":
        """Convert domain model to response schema."""
        return cls.model_validate(domain_model)

    def to_dict(self) -> dict:
        """Convert response to dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)
