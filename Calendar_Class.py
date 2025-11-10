"""
New Simple Calendar Class

This is a much simpler version of the Calendar class that uses the service pattern.
Instead of doing everything itself, it delegates to the CalendarService for business logic.

What this class does:
- Provides a simple interface for GUI classes to use
- Handles date calculations and utilities
- Coordinates with the CalendarService for event operations
- Maintains compatibility with existing GUI code

What it doesn't do anymore:
- Direct database operations (handled by repository)
- Complex event management (handled by service)
- Event validation (handled by service)
"""

import datetime
import calendar
from typing import List, Tuple, Optional
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase
from Event_Class import Event


class Calendar:
    """
    Simplified Calendar class that uses the service pattern.

    This class provides a clean interface for GUI classes while delegating
    the complex business logic to the CalendarService.
    """

    def __init__(self, calendar_service: CalendarService = None):
        """
        Initialize the calendar with a service.

        Args:
            calendar_service (CalendarService, optional): Service to use for business logic.
                                                        Creates a default one if not provided.
        """
        if calendar_service is None:
            # Create default service with SQLite repository
            repository = CalendarDatabase()
            calendar_service = CalendarService(repository)

        self.service = calendar_service

    # === EVENT OPERATIONS (delegate to service) ===

    def create_event(self,
                     title: str,
                     date: datetime.date,
                     start_time: str = "",
                     end_time: str = "",
                     description: str = "",
                     is_all_day: bool = False,
                     is_recurring: bool = False,
                     recurrence_pattern: str = "") -> Tuple[bool, str, Optional[int]]:
        """
        Create a new event.

        Args:
            title (str): Event title
            date (datetime.date): Event date
            start_time (str): Start time (optional for all-day events)
            end_time (str): End time (optional for all-day events)
            description (str): Event description
            is_all_day (bool): Whether this is an all-day event
            is_recurring (bool): Whether this event repeats
            recurrence_pattern (str): How the event repeats

        Returns:
            Tuple[bool, str, Optional[int]]: (success, message, event_id)
        """
        return self.service.create_event(
            title, date, start_time, end_time, description,
            is_all_day, is_recurring, recurrence_pattern
        )

    def get_events_for_month(self, year: int, month: int) -> List[Event]:
        """Get all events for a specific month."""
        return self.service.get_events_for_month(year, month)

    def get_events_for_date(self, date: datetime.date) -> List[Event]:
        """Get all events for a specific date."""
        return self.service.get_events_for_date(date)

    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get a specific event by its ID."""
        return self.service.get_event_by_id(event_id)

    def update_event(self, event_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Update an existing event.

        Args:
            event_id (int): ID of event to update
            **kwargs: Fields to update (title, date, start_time, end_time, etc.)

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return self.service.update_event(event_id, **kwargs)

    def delete_event(self, event_id: int) -> Tuple[bool, str]:
        """Delete an event."""
        return self.service.delete_event(event_id)

    def has_events_on_date(self, date: datetime.date) -> bool:
        """Check if there are events on a specific date."""
        return self.service.has_events_on_date(date)

    # === DATE UTILITIES ===

    def get_today(self) -> datetime.date:
        """Get today's date."""
        return self.service.get_today()

    def get_current_month_year(self) -> Tuple[int, int]:
        """
        Get current month and year.

        Returns:
            Tuple[int, int]: (month, year)
        """
        today = self.get_today()
        return today.month, today.year

    def calculate_next_month(self, year: int, month: int) -> Tuple[int, int]:
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

    def calculate_previous_month(self, year: int, month: int) -> Tuple[int, int]:
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

    def calculate_week_start(self, date: datetime.date) -> datetime.date:
        """
        Calculate the start of the week (Sunday) for a given date.

        Args:
            date (datetime.date): Date to calculate week start for

        Returns:
            datetime.date: The Sunday that starts the week containing the given date
        """
        days_since_sunday = (date.weekday() + 1) % 7
        return date - datetime.timedelta(days=days_since_sunday)

    def calculate_week_dates(self, week_start: datetime.date) -> List[datetime.date]:
        """
        Calculate all 7 dates in a week starting from the given date.

        Args:
            week_start (datetime.date): The Sunday that starts the week

        Returns:
            List[datetime.date]: List of 7 dates for the week
        """
        return [week_start + datetime.timedelta(days=i) for i in range(7)]

    # === FORMATTING UTILITIES ===

    def format_month_display_name(self, year: int, month: int) -> str:
        """
        Format month and year for display.

        Args:
            year (int): Year
            month (int): Month (1-12)

        Returns:
            str: Formatted month name and year (e.g., "November 2025")
        """
        return f"{calendar.month_name[month]} {year}"

    def format_week_display_name(self, week_start: datetime.date, week_end: datetime.date) -> str:
        """
        Format week range for display.

        Args:
            week_start (datetime.date): Start of week (Sunday)
            week_end (datetime.date): End of week (Saturday)

        Returns:
            str: Formatted week range
        """
        if week_start.year == week_end.year:
            if week_start.month == week_end.month:
                return f"{calendar.month_name[week_start.month]} {week_start.day}-{week_end.day}, {week_start.year}"
            else:
                return f"{calendar.month_name[week_start.month]} {week_start.day} - {calendar.month_name[week_end.month]} {week_end.day}, {week_start.year}"
        else:
            return f"{calendar.month_name[week_start.month]} {week_start.day}, {week_start.year} - {calendar.month_name[week_end.month]} {week_end.day}, {week_end.year}"

    def format_date_for_display(self, date: datetime.date) -> str:
        """Format a date for nice display."""
        return self.service.format_date_for_display(date)

    # === COMPATIBILITY METHODS ===
    # These methods help maintain compatibility with existing GUI code

    def get_month_calendar(self, year: int, month: int) -> 'MonthView':
        """
        Get a month view object for compatibility with existing code.

        Args:
            year (int): Year
            month (int): Month

        Returns:
            MonthView: Object containing month data
        """
        events = self.get_events_for_month(year, month)
        return MonthView(year, month, events)


class MonthView:
    """
    Simple data container for month information.

    This replaces the old MonthCalendar class with a simpler approach.
    It's just a container for month data, not a complex class with database operations.
    """

    def __init__(self, year: int, month: int, events: List[Event]):
        """
        Initialize a month view with events.

        Args:
            year (int): Year
            month (int): Month
            events (List[Event]): All events in this month
        """
        self.year = year
        self.month = month
        self.events = {event.event_id: event for event in events}
        self.events_by_date = self._group_events_by_date(events)

    def _group_events_by_date(self, events: List[Event]) -> dict:
        """
        Group events by their date.

        Args:
            events (List[Event]): List of events to group

        Returns:
            dict: Dictionary mapping date strings to lists of event IDs
        """
        grouped = {}
        for event in events:
            date_str = event.date
            if date_str not in grouped:
                grouped[date_str] = []
            # Convert event_id to int if it's not None
            event_id = int(event.event_id) if event.event_id is not None else None
            if event_id is not None:
                grouped[date_str].append(event_id)
        return grouped

    def get_events_for_date(self, date_str: str) -> List[Event]:
        """
        Get all events for a specific date.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            List[Event]: Events on that date
        """
        event_ids = self.events_by_date.get(date_str, [])
        return [self.events[event_id] for event_id in event_ids if event_id in self.events]

    def get_event(self, event_id: int) -> Optional[Event]:
        """
        Get a specific event by ID.

        Args:
            event_id (int): Event ID to look for

        Returns:
            Event or None: The event if found in this month
        """
        return self.events.get(event_id)