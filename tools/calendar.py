from .models import AddEventCalendarInput, ListEventsCalendarInput, ConvertWeekdayToDateInput, ListEventsCalendarOutput, RemoveEventCalendarInput
from .utils import load_json, save_json
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
import datetime

events_path = 'data/calendar.json'


@tool
def list_events(
    data: ListEventsCalendarInput, 
    config: RunnableConfig
) -> str | ListEventsCalendarOutput:
    """
    List events from the user's calendar.
    
    Input:
    - date: ISO date (YYYY-MM-DD)
    - time: Optional time filter (HH:MM)
    - config: RunnableConfig to access user information

    Output:
    - If events are found, returns ListEventsCalendarOutput with weekday and schedule.
    - If no events are found, returns a string message indicating no events.
    """
    asked_date = data.date
    user_name = config['configurable']['user']
    # user_name = data.user
    full_data = load_json(events_path) or {}
    user_cal = full_data.get(user_name, {})
    date_events = user_cal.get(asked_date, {})
    filtered_events = []
    if date_events:
        if data.time:
            for event in date_events.get('schedule', []):
                if event['time'] == data.time:
                    filtered_events.append(event)
        else:
            filtered_events = date_events.get('schedule', [])
    if not filtered_events:
        return f"No events found for {user_name} on {data.date} at {data.time or 'any time'}."
    return ListEventsCalendarOutput(
        weekday=date_events.get('weekday', 'unknown'),
        schedule=filtered_events
    )

@tool
def add_event(
    data: AddEventCalendarInput, 
    config: RunnableConfig
) -> str:
    """
    Add an event to the user's calendar.

    Input:
    - date: ISO date (YYYY-MM-DD)
    - time: Time (HH:MM)
    - title: Event title

    Output:
    - str: Confirmation message of the added event.
    """
    full_data = load_json(events_path) or {}
    user = config['configurable']['user']
    # user = data.user
    user_cal = full_data.setdefault(user, {})
    date_entry = user_cal.setdefault(
        data.date,
        {
            "weekday": datetime.datetime.strptime(data.date, "%Y-%m-%d").strftime("%A").lower(),
            "schedule": []
        }
    )
    schedule = date_entry.setdefault("schedule", [])
    if any(e["time"] == data.time for e in schedule):
        return f"Event already exists for {user} on {data.date} at {data.time}."
    schedule.append({"time": data.time, "title": data.title})
    # Sort by time to keep consistency
    schedule.sort(key=lambda e: e["time"])
    save_json(events_path, full_data)
    return f"Event '{data.title}' added for {user} on {data.date} at {data.time}."

@tool
def delete_event(
    data: RemoveEventCalendarInput, 
    config: RunnableConfig
) -> str:
    """
    Remove an event from the calendar by exact title.

    Input:
    - date: ISO date (YYYY-MM-DD)
    - title: Event title
    - config: RunnableConfig to access user information

    Output:
    - str: Confirmation message of the removed event or error if not found.
    """
    full_data = load_json(events_path) or {}
    user = config['configurable']['user']
    # user = data.user
    user_cal = full_data.get(user)
    if not user_cal:
        return f"No calendar found for {user}."
    date_entry = user_cal.get(data.date)
    if not date_entry:
        return f"No events found for {user} on {data.date}."
    schedule = date_entry.get("schedule", [])
    original_len = len(schedule)
    schedule = [e for e in schedule if e["title"].lower() != data.title.lower()]
    if len(schedule) == original_len:
        return f"Event '{data.title.lower()}' not found for {user} on {data.date}."
    date_entry["schedule"] = schedule
    save_json(events_path, full_data)
    return f"Event '{data.title.lower()}' removed for {user} on {data.date}."

@tool
def get_current_date():
    """
    Returns the current date in format YYYY-MM-DD, e.g., "2025-04-01" and the current day.

    Returns:
    str: Current date in format YYYY-MM-DD (ex: "2025-04-01") and the current day.
    """
    now = datetime.datetime.now()
    return f"{now.strftime('%Y-%m-%d')} (day: {now.strftime('%A').lower()})"

@tool 
def convert_weekday_to_date(
    data: ConvertWeekdayToDateInput
) -> str:
    """
    Convert a weekday name to the next date it falls on.

    Input:
    - weekday: Weekday name (e.g., 'monday')

    Output:
    - str: The next date in format YYYY-MM-DD corresponding to the given weekday.
    """
    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6
    }
    today = datetime.datetime.now()
    today_weekday = today.weekday()
    target_weekday = weekdays[data.weekday]
    days_ahead = target_weekday - today_weekday
    if days_ahead <= 0:
        days_ahead += 7
    target_date = today + datetime.timedelta(days=days_ahead)
    # formato YYYY-MM-DD
    return target_date.strftime("%Y-%m-%d")