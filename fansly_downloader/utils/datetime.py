"""Time Manipulation"""


import time


def get_time_format() -> int:
    """Detect and return 12 vs 24 hour time format usage.
    
    :return: 12 or 24
    :rtype: int
    """
    return 12 if ('AM' in time.strftime('%X') or 'PM' in time.strftime('%X')) else 24


def get_timezone_offset():
    """Returns the local timezone offset from UTC.
    
    :return: The tuple (diff_from_utc, hours_in_seconds)
    :rtype: Tuple[int, int]
    """
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone

    diff_from_utc = int(offset / 60 / 60 * -1)
    hours_in_seconds = diff_from_utc * 3600 * -1

    return diff_from_utc, hours_in_seconds


def get_adjusted_datetime(epoch_timestamp: int):
    """Converts an epoch timestamp to the time of the
    local computers' timezone.
    """
    diff_from_utc, hours_in_seconds = get_timezone_offset()

    adjusted_timestamp = epoch_timestamp + diff_from_utc * 3600
    adjusted_timestamp += hours_in_seconds

    # start of strings are ISO 8601; so that they're sortable by Name after download
    if get_time_format() == 24:
        return time.strftime("%Y-%m-%d_at_%H-%M", time.localtime(adjusted_timestamp))

    else:
        return time.strftime("%Y-%m-%d_at_%I-%M-%p", time.localtime(adjusted_timestamp))
