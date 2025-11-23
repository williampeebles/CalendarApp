"""
Week View Service

This service handles all week-specific calendar operations for the WeekViewGUI.
It includes week navigation, formatting, and event retrieval for week views.
"""

import datetime


class WeekViewService:
    """
    Service class for week view operations.
    
    Handles:
    - Week start calculation (Sunday-based)
    - Week date range calculation
    - Week display formatting
    - Event checking for dates
    - Event retrieval for dates
    """
    
    def __init__(self, calendar_service):
        """
        Initialize the WeekViewService.
        
        Args:
            calendar_service: CalendarService instance for shared operations
        """
        self.calendar_service = calendar_service
        self.DATABASE_DATE_FORMAT = "%Y-%m-%d"
    
    def calculate_week_start(self, date):
        """
        Calculate the start of the week (Sunday) for a given date.

        Args:
            date (datetime.date): Date to calculate week start for

        Returns:
            datetime.date: The Sunday that starts the week containing the given date
        """
        days_since_sunday = (date.weekday() + 1) % 7
        return date - datetime.timedelta(days=days_since_sunday)
    
    def calculate_week_dates(self, week_start):
        """
        Calculate all 7 dates in a week starting from the given date.

        Args:
            week_start (datetime.date): The Sunday that starts the week

        Returns:
            List[datetime.date]: List of 7 dates for the week
        """
        return [week_start + datetime.timedelta(days=i) for i in range(7)]
    
    def format_week_display_name(self, week_start, week_end):
        """
        Format week range for display.

        Args:
            week_start (datetime.date): Start of week (Sunday)
            week_end (datetime.date): End of week (Saturday)

        Returns:
            str: Formatted week range
        """
        import calendar
        
        if week_start.year == week_end.year:
            if week_start.month == week_end.month:
                return f"{calendar.month_name[week_start.month]} {week_start.day}-{week_end.day}, {week_start.year}"
            else:
                return f"{calendar.month_name[week_start.month]} {week_start.day} - {calendar.month_name[week_end.month]} {week_end.day}, {week_start.year}"
        else:
            return f"{calendar.month_name[week_start.month]} {week_start.day}, {week_start.year} - {calendar.month_name[week_end.month]} {week_end.day}, {week_end.year}"
    
    def has_events_on_date(self, date: datetime.date) -> bool:
        """
        Check if there are any events on a specific date.

        Args:
            date (datetime.date): Date to check

        Returns:
            bool: True if there are events, False otherwise
        """
        events = self.get_events_for_date(date)
        return len(events) > 0
    
    def get_events_for_date(self, date):
        """
        Get all events for a specific date.

        Args:
            date (datetime.date): The date to get events for

        Returns:
            List[Event]: All events on that date
        """
        date_str = date.strftime(self.DATABASE_DATE_FORMAT)
        event_dicts = self.calendar_service.repository.get_events_for_date(date_str)
        return [self.calendar_service._dict_to_event(event_dict) for event_dict in event_dicts]
