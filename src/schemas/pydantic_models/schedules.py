from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class NewScheduleModel(BaseModel):
    group_id: int = Field(alias="groupId", description="ID of the group")
    schedule_date: datetime = Field(
        alias="scheduleDate", description="Date of the schedules"
    )


class SearchScheduleModel(BaseModel):
    year: Optional[int] = Field(description="Year of the schedules")
    month: Optional[int] = Field(description="Month of the schedules")
    group_id: Optional[int] = Field(alias="groupId", description="ID of the group")

    class Config:
        validate_by_name = True
