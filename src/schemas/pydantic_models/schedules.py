from datetime import datetime
from pydantic import BaseModel, Field


class NewScheduleModel(BaseModel):
    group_id: int = Field(alias="groupId", description="ID of the group")
    schedule_date: datetime = Field(alias="scheduleDate", description="Date of the schedules")