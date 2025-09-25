from .models import ConvertWeekdayToDateInput, RetrieveDeskGeneralInfoInput, ReserveDeskInput, ReleaseDeskInput
from .utils import load_json, save_json
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig

import datetime

desk_info_path = 'data/desk_info.json'
desk_reservations_path = 'data/desk_reservations.json'



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


@tool
def retrieve_desk_general_info(
    data: RetrieveDeskGeneralInfoInput
) -> str:
    """
    Retrieve general information about a desk given its ID.

    Input:
    - data.desk_id: The unique identifier of the desk.

    Output:
    - str: General information about the desk.
    """
    desks_data = load_json(desk_info_path) or {}
    desk_id = data.desk_id
    desk_info = desks_data.get(desk_id)
    if not desk_info:
        return f"No information found for desk ID: {desk_id}."
    allowed = desk_info.get('allowed_users', [])
    if isinstance(allowed, set):
        allowed = list(allowed)
    info = (
        f"Desk ID: {desk_id}\n"
        f"Location: {desk_info.get('location', 'N/A')}\n"
        f"Description: {desk_info.get('description', 'N/A')}\n"
        f"Allowed Users: {', '.join(allowed)}"
    )
    return info

@tool
def reserve_desk(
    data: ReserveDeskInput,
    config: RunnableConfig
) -> str:
    """
    Reserve a desk for a user on a specific date.

    Input:
    - date: ISO date (YYYY-MM-DD)
    - desk_id: The unique identifier of the desk (A0, ..., A9, B0, ... B9)
    - user: User name (e.g., 'alice')

    Output:
    - str: Confirmation message of the reservation or error if not possible.
    """
    reservations = load_json(desk_reservations_path) or {}
    date_entry = reservations.get(data.date)
    if not date_entry:
        return f"Cannot reserve: date {data.date} not available."

    day_res = date_entry.get("reservations", {})
    if data.desk_id not in day_res:
        return f"Desk ID {data.desk_id} does not exist."

    slot = day_res[data.desk_id]
    if not slot.get("is_free", True):
        return f"Desk {data.desk_id} is already reserved for {data.date} by {slot.get('user')}."

    user = config["configurable"]["user"]
    # user = data.user
    for d_id, d_slot in day_res.items():
        if not d_slot.get("is_free", True) and d_slot.get("user") == user:
            return f"Reservation already found for this day and this user. You have reserved desk {d_id} on {data.date}."

    desk_info = load_json(desk_info_path) or {}
    meta = desk_info.get(data.desk_id)
    if meta:
        allowed = meta.get("allowed_users")
        if allowed and user not in allowed:
            return f"User {user} not allowed to reserve desk {data.desk_id}."

    slot["is_free"] = False
    slot["user"] = user
    save_json(desk_reservations_path, reservations)
    return f"Desk {data.desk_id} reserved for {user} on {data.date}."

@tool
def release_desk(
    data: ReleaseDeskInput, 
    config: RunnableConfig
) -> str:
    """
    Release a desk reservation.

    Input:
    - date: ISO date (YYYY-MM-DD)
    - desk_id: The unique identifier of the desk (A0, ..., A9, B0, ... B9)
    - user: User name (e.g., 'alice')
    - config: RunnableConfig with 'user' key in 'configurable' dict

    Output:
    - str: Confirmation message of the release or error if not possible.
    """
    reservations = load_json(desk_reservations_path) or {}
    date_entry = reservations.get(data.date)
    if not date_entry:
        return f"Cannot release: date {data.date} not available."

    day_res = date_entry.get("reservations", {})
    if data.desk_id not in day_res:
        return f"Desk ID {data.desk_id} does not exist."

    slot = day_res[data.desk_id]
    if slot.get("is_free", True):
        return f"Desk {data.desk_id} is already free for {data.date}."
    user = config["configurable"]["user"]
    # user = data.user
    if slot.get("user") != user:
        return f"Cannot release: Desk {data.desk_id} is reserved by {slot.get('user')}, not {user}."
    slot["is_free"] = True
    slot["user"] = None
    save_json(desk_reservations_path, reservations)
    return f"Desk {data.desk_id} released for {user} on {data.date}."

@tool
def get_all_reserved_desks(
    config: RunnableConfig
) -> str:
    """
    Get all reserved desks.

    Input:
    - config: RunnableConfig with 'user' key in 'configurable' dict
    Output:
    - str: List of all reserved desks for a certain user.
    """
    user = config["configurable"]["user"]
    # user = data.user
    reservations = load_json(desk_reservations_path) or {}
    all_reserved = []
    for date, date_entry in reservations.items():
        day_res = date_entry.get("reservations", {})
        for desk_id, slot in day_res.items():
            if not slot.get("is_free", True) and slot.get("user") == user:
                all_reserved.append(f"Date: {date}, Desk ID: {desk_id}")
    if not all_reserved:
        return f"No reservations found for user {user}."
    return "\n".join(all_reserved)