from datetime import date, timedelta

class SaudiArabia:
    """
    Simple Saudi Arabia working days calendar (Sunday–Thursday).
    - Weekends: Friday (4) and Saturday (5)
    - Working days: Sunday (6), Monday–Thursday (0–3)
    """

    def is_working_day(self, day: date) :
        """Return True if the given day is a working day."""
        # weekday(): Monday=0 ... Sunday=6
        return day.weekday() not in (4, 5)  # Exclude Friday & Saturday

    def add_working_days(self, start_date: date, working_days: int) :
        """
        Add or subtract a number of working days from a given date.
        Skips weekends (Friday–Saturday).
        """
        current_date = start_date
        days_added = 0
        step = 1 if working_days >= 0 else -1

        while days_added != working_days:
            current_date += timedelta(days=step)
            if self.is_working_day(current_date):
                days_added += step
        return current_date


def get_monthly_schedule(year: int, month: int) :
    """
    Returns key operational dates for the given month based on Saudi working days.
    """
    calendar = SaudiArabia()
    first_day_of_month = date(year, month, 1)

    send_day = calendar.add_working_days(first_day_of_month, 0)
    reminder_day = calendar.add_working_days(send_day, 2)
    last_submission_day = calendar.add_working_days(send_day, 4)
    report_day = calendar.add_working_days(send_day, 5)

    return {
        "send_day": send_day,
        "reminder_day": reminder_day,
        "last_submission_day": last_submission_day,
        "report_day": report_day
    }
