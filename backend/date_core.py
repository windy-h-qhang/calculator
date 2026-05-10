from datetime import date, datetime, timedelta


class DateCalculator:
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()

    @classmethod
    def difference(cls, start_date, end_date, include_end=False):
        start = cls.parse_date(start_date)
        end = cls.parse_date(end_date)
        days = (end - start).days
        if include_end and days >= 0:
            days += 1
        elif include_end and days < 0:
            days -= 1
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "days": days,
            "weeks": days / 7,
            "absolute_days": abs(days),
        }

    @classmethod
    def add_days(cls, start_date, days, weekdays_only=False):
        current = cls.parse_date(start_date)
        step = 1 if int(days) >= 0 else -1
        remaining = abs(int(days))
        if not weekdays_only:
            result = current + timedelta(days=int(days))
            return {"start": current.isoformat(), "result": result.isoformat(), "days": int(days)}

        while remaining:
            current += timedelta(days=step)
            if current.weekday() < 5:
                remaining -= 1
        return {"start": cls.parse_date(start_date).isoformat(), "result": current.isoformat(), "days": int(days)}

    @classmethod
    def add_ymd(cls, start_date, years=0, months=0, days=0):
        start = cls.parse_date(start_date)
        month = start.month - 1 + int(months) + int(years) * 12
        year = start.year + month // 12
        month = month % 12 + 1
        day = min(start.day, cls.days_in_month(year, month))
        result = date(year, month, day) + timedelta(days=int(days))
        return {"start": start.isoformat(), "result": result.isoformat()}

    @staticmethod
    def days_in_month(year, month):
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        return (next_month - timedelta(days=1)).day
