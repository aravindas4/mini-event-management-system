from fastapi import HTTPException


class BaseController:
    """
    Base controller class that provides common functionality for all controllers.
    """

    def handle_not_found(self, message: str = "Resource not found"):
        raise HTTPException(status_code=404, detail=message)

    def handle_bad_request(self, message: str = "Bad request"):
        raise HTTPException(status_code=400, detail=message)
