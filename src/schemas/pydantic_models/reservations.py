from datetime import datetime
from pydantic import BaseModel, Field


class NewReservationModel(BaseModel):
    date: datetime = Field(..., description="Date of the reservation")