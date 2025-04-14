from datetime import datetime

from typeguard import typechecked


@typechecked
def get_time_string() -> str:
    """
    Get current time string.
    :return: String like `20250411091422`.
    """
    current_time = datetime.now()
    time_str = current_time.strftime("%Y%m%d%H%M%S")
    return time_str


@typechecked
def get_time_iso_string() -> str:
    now = datetime.now()
    formatted_date = now.isoformat()
    return formatted_date
