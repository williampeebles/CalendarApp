"""
Day View Service

This service handles all day-specific calendar operations for the DayViewGUI.
It includes event CRUD operations, date formatting, and event retrieval for specific dates.
"""

import datetime


class DayViewService:
    """
    Service class for day view operations.
    
    Handles:
    - Date formatting for display
    - Event retrieval for specific dates
    - Event creation with validation
    - Event updating
    - Event deletion
    """
    
    def __init__(self, calendar_service):
        """
        Initialize the DayViewService.
        
        Args:
            calendar_service: CalendarService instance for shared operations
        """
        self.calendar_service = calendar_service
        self.DATE_FORMAT = "%d-%m-%Y"  # DD-MM-YYYY (16-11-2025)
        self.DATABASE_DATE_FORMAT = "%Y-%m-%d"  # Database internal format (YYYY-MM-DD)
    
    def format_date_for_display(self, date: datetime.date) -> str:
        """
        Format a date for display to users in DD-MM-YYYY format.

        Args:
            date (datetime.date): Date to format

        Returns:
            str: Date string in DD-MM-YYYY format
        """
        return date.strftime(self.DATE_FORMAT)  # e.g., "16-11-2025"
    
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
    
    def create_event(self,
                     title,
                     date,
                     start_time="",
                     end_time="",
                     description="",
                     is_all_day=False,
                     is_recurring=False,
                     recurrence_pattern=""):
        """
        Create a new event with validation.
        Delegates to CalendarService for the actual creation.

        Args:
            title (str): Event title (required)
            date (datetime.date): Event date (required)
            start_time (str): Start time (optional for all-day events)
            end_time (str): End time (optional for all-day events)
            description (str): Event description (optional)
            is_all_day (bool): Whether this is an all-day event
            is_recurring (bool): Whether this event repeats
            recurrence_pattern (str): How the event repeats (if recurring)

        Returns:
            Tuple[bool, str, Optional[int]]: (success, message, event_id)
        """
        return self.calendar_service.create_event(
            title, date, start_time, end_time, description,
            is_all_day, is_recurring, recurrence_pattern
        )
    
    def update_event(self,
                     event_id,
                     title=None,
                     date=None,
                     start_time=None,
                     end_time=None,
                     description=None,
                     is_all_day=None,
                     is_recurring=None,
                     recurrence_pattern=None):
        """
        Update an existing event.
        Delegates to CalendarService for the actual update.

        Args:
            event_id (int): ID of the event to update
            Other parameters: New values (None means don't change)

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return self.calendar_service.update_event(
            event_id, title, date, start_time, end_time, 
            description, is_all_day, is_recurring, recurrence_pattern
        )
    
    def delete_event(self, event_id, delete_all_recurring=False):
        """
        Delete an event. If it's a recurring event, can optionally delete all instances.
        Delegates to CalendarService for the actual deletion.

        Args:
            event_id (int): ID of the event to delete
            delete_all_recurring (bool): If True and event is recurring, delete all instances

        Returns:
            Tuple[bool, str]: (success, message)
        """
        return self.calendar_service.delete_event(event_id, delete_all_recurring)
