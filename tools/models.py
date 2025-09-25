from typing import Any
from enum import StrEnum
from pydantic import BaseModel, Field
from typing_extensions import Annotated

class PossibleDesks(StrEnum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    A6 = "A6"
    A7 = "A7"
    A8 = "A8"
    A9 = "A9"
    B0 = "B0"
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    B5 = "B5"
    B6 = "B6"
    B7 = "B7"
    B8 = "B8"
    B9 = "B9"

class PossibleWeekdays(StrEnum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"
    
class AppBaseModel(BaseModel):
    def json(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return super().model_dump(*args, **kwargs, by_alias=True, exclude_none=True, mode="json")

    def input(self) -> dict[str, Any]:
        return {"data": self}

class AddEventCalendarInput(AppBaseModel):
    date: str = Field(description="ISO date (YYYY-MM-DD)")
    time: str = Field(description="Time (HH:MM)")
    title: str = Field(description="Event title")

class RemoveEventCalendarInput(AppBaseModel):
    date: str = Field(description="ISO date (YYYY-MM-DD)")
    title: str = Field(description="Event title")

class ListEventsCalendarInput(AppBaseModel):
    date: str = Field(description="ISO date (YYYY-MM-DD)")
    time : Annotated[str | None, Field(description="Optional time filter (HH:MM)")] = None

class ListEventsCalendarOutput(AppBaseModel):
    weekday: PossibleWeekdays = Field(description="Day of the week (e.g., 'monday')")
    schedule: list[dict[str, str]] = Field(description="List of events with 'title' and 'time'")

class ConvertWeekdayToDateInput(AppBaseModel):
    weekday: PossibleWeekdays = Field(description="Weekday name (e.g., 'monday')")

class RetrieveDeskGeneralInfoInput(AppBaseModel):
    desk_id: PossibleDesks = Field(description="The unique identifier of the desk (A0, ..., A9, B0, ... B9)")

class ReserveDeskInput(AppBaseModel):
    date: str = Field(description="ISO date (YYYY-MM-DD)")
    desk_id: PossibleDesks = Field(description="The unique identifier of the desk (A0, ..., A9, B0, ... B9)")
    
class ReleaseDeskInput(AppBaseModel):
    date: str = Field(description="ISO date (YYYY-MM-DD)")
    desk_id: PossibleDesks = Field(description="The unique identifier of the desk (A0, ..., A9, B0, ... B9)")