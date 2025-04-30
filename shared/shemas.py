from pydantic import BaseModel


# Define the schema for a travel request
class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float