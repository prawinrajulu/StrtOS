from app.models.database import Client as ClientModel
from app.clients.schemas import ClientStatusEnum

class ClientValidator:
    """Business validation rules for Client Management."""
    
    @staticmethod
    def validate_create_payload(name: str, industry: str):
        if not name or not name.strip():
            raise ValueError("Client name cannot be empty.")
        if not industry or not industry.strip():
            raise ValueError("Industry cannot be empty.")

    @staticmethod
    def validate_budget(budget: float):
        if budget is not None and budget < 0:
            raise ValueError("Monthly budget cannot be negative.")
