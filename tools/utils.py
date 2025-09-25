from typing import Any
import json
import datetime


def load_json(file_path: str) -> Any:
    with open(file_path, 'r') as f:
        return json.load(f)
    
def save_json(file_path: str, data: Any) -> None:
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)


def get_current_date():
    """
    Returns the current date in format YYYY-MM-DD, e.g., "2025-04-01" and the current day.

    Returns:
    str: Current date in format YYYY-MM-DD (ex: "2025-04-01") and the current day.
    """
    now = datetime.datetime.now()
    return f"{now.strftime('%Y-%m-%d')} (day: {now.strftime('%A').lower()})"