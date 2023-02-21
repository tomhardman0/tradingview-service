from datetime import datetime


def is_market_opening(time):
    if (time.hour == 7 and time.minute >= 50) or (
        time.hour == 8 and 0 <= time.minute <= 30
    ):
        return True

    return False


def is_end_of_week(time):
    if time.weekday() == 4 and time.hour >= 21:
        return True

    return False


def is_start_of_week(time):
    if time.weekday() == 6 and time.hour == 22:
        return True

    return False


def should_order():
    time = datetime.now()
    if is_market_opening(time) or is_end_of_week(time) or is_start_of_week(time):
        return False

    return True
