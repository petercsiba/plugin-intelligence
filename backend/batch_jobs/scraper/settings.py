from datetime import datetime, timedelta


def should_save_large_fields(p_date: str) -> bool:
    date_format = "%Y-%m-%d"
    input_date = datetime.strptime(p_date, date_format)
    seven_days_ago = datetime.now() - timedelta(days=7)
    return input_date > seven_days_ago
