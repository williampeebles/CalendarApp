"""
Agenda View Service

This service handles all agenda-specific calendar operations for the AgendaViewGUI.
It includes event retrieval across date ranges and event management operations.
"""


class AgendaViewService:
    """
    Service class for agenda view operations.
    
    Handles:
    - Retrieving all events across multiple months
    - Getting specific events by ID
    - Event deletion operations
    """
    
    def __init__(self, calendar_service):
        """
        Initialize the AgendaViewService.
        
        Args:
            calendar_service: CalendarService instance for shared operations
        """
        self.calendar_service = calendar_service
    
    def get_all_events(self, months_before=6, months_after=6):
        """
        Get all events within a date range relative to today.

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
            month_events = self._get_events_for_month(target_year, target_month)
            all_events.extend(month_events)

        # Sort events by date and time
        all_events.sort(key=lambda event: (event.date, event.start_time))

        return all_events
    
    def _get_events_for_month(self, year, month):
        """
        Get all events for a specific month.
        Internal helper method.

        Args:
            year (int): Year (e.g., 2025)
            month (int): Month (1-12)

        Returns:
            List[Event]: All events in that month
        """
        event_dicts = self.calendar_service.repository.get_events_for_month(year, month)
        return [self.calendar_service._dict_to_event(event_dict) for event_dict in event_dicts]
    
    def get_event_by_id(self, event_id):
        """
        Get a specific event by its ID.

        Args:
            event_id (int): The event ID to look for

        Returns:
            Event or None: The event if found, None otherwise
        """
        event_dict = self.calendar_service.repository.get_event_by_id(event_id)
        if event_dict:
            return self.calendar_service._dict_to_event(event_dict)
        return None
    
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
