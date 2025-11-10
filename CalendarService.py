"""
Calendar Service

This file contains the logic for the calendar application.
It coordinates between the database and the rest of the application.

The service handles:
- Creating new events with validation
- Updating existing events
- Deleting events
- Retrieving events in various ways
- Business rules and validation

Think of this as the "brain" of the calendar - it makes the decisions
about what's allowed and what isn't.
"""

import datetime
from Calendar_Database_Class import CalendarDatabase
from Event_Class import Event


class CalendarService:
    """
    Service class that handles all calendar logic.

    This class coordinates between the database and the user interface.
    It contains all the rules about what makes a valid event, how to create events,
    and how to manage the calendar data.
    """

    def __init__(self, database: CalendarDatabase):
        """
        Initialize the service with a database for data storage.

        Args:
            database (CalendarDatabase): Database for storing/retrieving events
        """
        self.repository = database

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
                - success: True if event created successfully
                - message: Success or error message
                - event_id: ID of created event (None if failed)
        """
        # Validate the input data
        is_valid, error_message = self._validate_event_data(
            title, date, start_time, end_time, is_all_day
        )

        if not is_valid:
            return False, error_message, None

        try:
            # Convert date to string format for storage
            date_str = date.strftime("%Y-%m-%d")

            # Handle all-day events
            if is_all_day:
                start_time = "All Day"
                end_time = "All Day"

            # Create the event object without event_id (database will generate it)
            event = Event(
                event_id=None,  # Will be set by database
                title=title,
                date=date_str,
                start_day=date_str,  # For single-day events, same as date
                end_day=date_str,  # For single-day events, same as date
                start_time=start_time,
                end_time=end_time,
                description=description,
                is_recurring=is_recurring,
                recurrence_pattern=recurrence_pattern if is_recurring else None,
                is_all_day=is_all_day
            )

            # Save to repository and get the generated ID
            event_id = self.repository.save_event(event)
            if event_id > 0:
                return True, "Event created successfully!", event_id
            else:
                return False, "Failed to save event to database", None

        except Exception as e:
            return False, f"Error creating event: {str(e)}", None

    def get_events_for_month(self, year, month):
        """
        Get all events for a specific month.

        Args:
            year (int): Year (e.g., 2025)
            month (int): Month (1-12)

        Returns:
            List[Event]: All events in that month
        """
        return self.repository.get_events_for_month(year, month)

    def get_events_for_date(self, date):
        """
        Get all events for a specific date.

        Args:
            date (datetime.date): The date to get events for

        Returns:
            List[Event]: All events on that date
        """
        date_str = date.strftime("%Y-%m-%d")
        return self.repository.get_events_for_date(date_str)

    def get_event_by_id(self, event_id):
        """
        Get a specific event by its ID.

        Args:
            event_id (int): The event ID to look for

        Returns:
            Event or None: The event if found, None otherwise
        """
        return self.repository.get_event_by_id(event_id)

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

        Args:
            event_id (int): ID of the event to update
            Other parameters: New values (None means don't change)

        Returns:
            Tuple[bool, str]: (success, message)
        """
        # First, get the existing event
        existing_event = self.repository.get_event_by_id(event_id)
        if not existing_event:
            return False, "Event not found"

        # Update only the fields that were provided
        if title is not None:
            existing_event.title = title
        if date is not None:
            date_str = date.strftime("%Y-%m-%d")
            existing_event.date = date_str
            existing_event.start_day = date_str
            existing_event.end_day = date_str
        if start_time is not None:
            existing_event.start_time = start_time
        if end_time is not None:
            existing_event.end_time = end_time
        if description is not None:
            existing_event.description = description
        if is_all_day is not None:
            existing_event.is_all_day = is_all_day
            if is_all_day:
                existing_event.start_time = "All Day"
                existing_event.end_time = "All Day"
        if is_recurring is not None:
            existing_event.is_recurring = is_recurring
        if recurrence_pattern is not None:
            existing_event.recurrence_pattern = recurrence_pattern

        # Validate the updated data
        date_obj = datetime.datetime.strptime(existing_event.date, "%Y-%m-%d").date()
        is_valid, error_message = self._validate_event_data(
            existing_event.title, date_obj,
            existing_event.start_time, existing_event.end_time,
            existing_event.is_all_day
        )

        if not is_valid:
            return False, error_message

        # Save the updated event
        if self.repository.update_event(existing_event):
            return True, "Event updated successfully!"
        else:
            return False, "Failed to update event in database"

    def delete_event(self, event_id):
        """
        Delete an event.

        Args:
            event_id (int): ID of the event to delete

        Returns:
            Tuple[bool, str]: (success, message)
        """
        if self.repository.delete_event(event_id):
            return True, "Event deleted successfully!"
        else:
            return False, "Event not found or could not be deleted"

    def _validate_event_data(self,
                             title,
                             date,
                             start_time,
                             end_time,
                             is_all_day):
        """
        Validate event data before creating or updating.

        Args:
            title (str): Event title
            date (datetime.date): Event date
            start_time (str): Start time
            end_time (str): End time
            is_all_day (bool): Whether it's all-day

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check title
        if not title or not title.strip():
            return False, "Event title is required and cannot be empty"

        # Check date (don't allow past dates)
        today = datetime.date.today()
        if date < today:
            return False, "Cannot create events for past dates"

        # For timed events, check that times are provided
        if not is_all_day:
            if not start_time or not start_time.strip():
                return False, "Start time is required for timed events"
            if not end_time or not end_time.strip():
                return False, "End time is required for timed events"

        return True, ""

    def get_today(self) -> datetime.date:
        """
        Get today's date.

        Returns:
            datetime.date: Today's date
        """
        return datetime.date.today()

    def format_date_for_display(self, date: datetime.date) -> str:
        """
        Format a date for nice display to users.

        Args:
            date (datetime.date): Date to format

        Returns:
            str: Nicely formatted date string
        """
        return date.strftime("%A, %B %d, %Y")  # e.g., "Saturday, November 09, 2025"

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