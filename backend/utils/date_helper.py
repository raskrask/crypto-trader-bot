from datetime import datetime, timedelta, timezone  
from dateutil.relativedelta import relativedelta

def get_days_ago(date):
    """
    指定された `date` が現在の日付の何日前かを計算する。
    """
    today = datetime.now(timezone.utc)
    delta = today - date
    return delta.days

def get_first_day_of_month(date):
    """ 指定された日付の月初の日を取得 """
    return date.replace(day=1)

def get_last_day_of_month(date):
    """ 指定された日付の月末の日を取得 """
    return (date.replace(day=1) + relativedelta(months=1)) - timedelta(days=1)

def get_first_day_of_next_month(date):
    """ 指定された日付の翌月の月初を取得 """
    return (date.replace(day=1) + relativedelta(months=1))