"""
Month View Service

This service handles all month-specific calendar operations for the MonthViewGUI.
It includes month navigation, formatting, and event retrieval for month views.
"""

import datetime
import calendar


class MonthViewService:
    """
    Service class for month view operations.
    
    Handles:
    - Month navigation (next/previous month)
    - Month display formatting
    - Current month/year retrieval
    - Event checking for dates
    - Event retrieval for months
    """
    
    def __init__(self, calendar_service):
        """
        Initialize the MonthViewService.
        
        Args:
            calendar_service: CalendarService instance for shared operations
        """
        self.calendar_service = calendar_service
        self.DATABASE_DATE_FORMAT = "%Y-%m-%d"
    
    def get_current_month_year(self):
        """
        Get current month and year.

        Returns:
            Tuple[int, int]: (month, year)
        """
        today = self.calendar_service.get_today()
        return today.month, today.year
    
    def calculate_next_month(self, year, month):
        """
        Calculate the next month and year.

        Args:
            year (int): Current year
            month (int): Current month

        Returns:
            Tuple[int, int]: (next_year, next_month)
        """
        if month < 12:
            return year, month + 1
        else:
            return year + 1, 1
    
    def calculate_previous_month(self, year, month):
        """
        Calculate the previous month and year.

        Args:
            year (int): Current year
            month (int): Current month

        Returns:
            Tuple[int, int]: (previous_year, previous_month)
        """
        if month > 1:
            return year, month - 1
        else:
            return year - 1, 12
    
    def format_month_display_name(self, year, month):
        """
        Format month and year for display.

        Args:
            year (int): Year
            month (int): Month (1-12)

        Returns:
            str: Formatted month name and year (e.g., "November 2025")
        """
        return f"{calendar.month_name[month]} {year}"
    
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
    
    def get_events_for_month(self, year, month):
        """
        Get all events for a specific month.

        Args:
            year (int): Year (e.g., 2025)
            month (int): Month (1-12)

        Returns:
            List[Event]: All events in that month
        """
        event_dicts = self.calendar_service.repository.get_events_for_month(year, month)
        return [self.calendar_service._dict_to_event(event_dict) for event_dict in event_dicts]
    
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
    
    def get_events_for_all_months(self, months_before=6, months_after=6):
        """
        Get all events within a date range relative to today.
        Used for filtering operations.

        Args:
            months_before (int): Number of months before today to include
            months_after (int): Number of months after today to include

        Returns:
            list: List of all Event objects sorted by date and time
        """
        all_events = []
        today = self.calendar_service.get_today()

        # Get events from specified range
        for month_offset in range(-months_before, months_after + 1):
            # Calculate target month/year
            target_year = today.year
            target_month = today.month + month_offset

            # Adjust for year boundaries
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            while target_month > 12:
                target_month -= 12
                target_year += 1

            # Get events for this month
            month_events = self.get_events_for_month(target_year, target_month)
            all_events.extend(month_events)

        # Sort events by date and time
        all_events.sort(key=lambda event: (event.date, event.start_time))

        return all_events
