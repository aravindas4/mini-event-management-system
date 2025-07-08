from typing import Any, Dict

from pydantic import BaseModel


class BaseRequest(BaseModel):
    """Base class for all request schemas"""

    def get(self) -> Dict[str, Any]:
        """Get validated data as a dictionary from the request."""
        return self.model_dump()
