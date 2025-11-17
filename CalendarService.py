"""
Calendar Service

This file contains the combined calendar logic for the application.
It coordinates between the database and the rest of the application.

The service handles:
- Creating new events with validation
- Updating existing events
- Deleting events
- Retrieving events in various ways
- Business rules and validation
- Date calculations and utilities
- Formatting for display

"""

import datetime
import calendar
from Calendar_Database_Class import CalendarDatabase
from Event_Class import Event



class CalendarService:
    """
    Unified service class that handles all calendar logic and operations.

    This class coordinates between the database and the user interface.
    It contains all the rules about what makes a valid event, how to create events,
    and how to manage the calendar data. It also provides date utilities and
    formatting methods.
    """

    def __init__(self, database=None):
        """
        Initialize the service with a database for data storage.

        Args:
            database (CalendarDatabase, optional): Database for storing/retrieving events.
                                                   Creates a default one if not provided.
        """
        if database is None:
            database = CalendarDatabase()
        self.repository = database

        self.DATE_FORMAT = "%d-%m-%Y"  # DD-MM-YYYY (16-11-2025)
        self.DATABASE_DATE_FORMAT = "%Y-%m-%d"  # Database internal format (YYYY-MM-DD)

    def _dict_to_event(self, event_dict):
        """
        Convert a database dictionary to an Event object.

        Args:
            event_dict (dict): Dictionary containing event data from database

        Returns:
            Event: Event object created from the dictionary
        """
        return Event(
            event_id=event_dict['event_id'],
            title=event_dict['title'],
            date=event_dict['date'],
            start_day=event_dict['start_day'],
            end_day=event_dict['end_day'],
            start_time=event_dict['start_time'],
            end_time=event_dict['end_time'],
            description=event_dict.get('description', ''),
            is_recurring=event_dict.get('is_recurring', False),
            recurrence_pattern=event_dict.get('recurrence_pattern'),
            is_all_day=event_dict.get('is_all_day', False)
        )

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
            # Convert date to string format for database storage
            date_str = date.strftime(self.DATABASE_DATE_FORMAT)

            # Handle all-day events
            if is_all_day:
                start_time = "All Day"
                end_time = "All Day"

            # Create event data dictionary for database
            event_data = {
                'title': title,
                'date': date_str,
                'start_day': date_str,  # For single-day events, same as date
                'end_day': date_str,  # For single-day events, same as date
                'start_time': start_time,
                'end_time': end_time,
                'description': description,
                'is_recurring': is_recurring,
                'recurrence_pattern': recurrence_pattern if is_recurring else None,
                'is_all_day': is_all_day
            }

            # Insert to repository and get the generated ID
            event_id = self.repository.insert_event(event_data)
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
        event_dicts = self.repository.get_events_for_month(year, month)
        return [self._dict_to_event(event_dict) for event_dict in event_dicts]

    def get_events_for_date(self, date):
        """
        Get all events for a specific date.

        Args:
            date (datetime.date): The date to get events for

        Returns:
            List[Event]: All events on that date
        """
        date_str = date.strftime(self.DATABASE_DATE_FORMAT)
        event_dicts = self.repository.get_events_for_date(date_str)
        return [self._dict_to_event(event_dict) for event_dict in event_dicts]

    def get_event_by_id(self, event_id):
        """
        Get a specific event by its ID.

        Args:
            event_id (int): The event ID to look for

        Returns:
            Event or None: The event if found, None otherwise
        """
        event_dict = self.repository.get_event_by_id(event_id)
        if event_dict:
            return self._dict_to_event(event_dict)
        return None

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
        event_dict = self.repository.get_event_by_id(event_id)
        if not event_dict:
            return False, "Event not found"

        # Update only the fields that were provided
        if title is not None:
            event_dict['title'] = title
        if date is not None:
            date_str = date.strftime(self.DATABASE_DATE_FORMAT)
            event_dict['date'] = date_str
            event_dict['start_day'] = date_str
            event_dict['end_day'] = date_str
        if start_time is not None:
            event_dict['start_time'] = start_time
        if end_time is not None:
            event_dict['end_time'] = end_time
        if description is not None:
            event_dict['description'] = description
        if is_all_day is not None:
            event_dict['is_all_day'] = is_all_day
            if is_all_day:
                event_dict['start_time'] = "All Day"
                event_dict['end_time'] = "All Day"
        if is_recurring is not None:
            event_dict['is_recurring'] = is_recurring
        if recurrence_pattern is not None:
            event_dict['recurrence_pattern'] = recurrence_pattern

        # Validate the updated data
        date_obj = datetime.datetime.strptime(event_dict['date'], self.DATABASE_DATE_FORMAT).date()
        is_valid, error_message = self._validate_event_data(
            event_dict['title'], date_obj,
            event_dict['start_time'], event_dict['end_time'],
            event_dict['is_all_day']
        )

        if not is_valid:
            return False, error_message

        # Save the updated event
        try:
            self.repository.update_event(event_dict)
            return True, "Event updated successfully!"
        except Exception as e:
            return False, f"Failed to update event: {str(e)}"

    def delete_event(self, event_id):
        """
        Delete an event.

        Args:
            event_id (int): ID of the event to delete

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            self.repository.delete_event(event_id)
            return True, "Event deleted successfully!"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Failed to delete event: {str(e)}"

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
        Format a date for display to users in DD-MM-YYYY format.

        Args:
            date (datetime.date): Date to format

        Returns:
            str: Date string in DD-MM-YYYY format
        """
        return date.strftime(self.DATE_FORMAT)  # e.g., "16-11-2025"

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
        today = self.get_today()

        # Get events from specified range
        for month_offset in range(-months_before, months_after + 1):
            # Calculate target month/year using existing utility
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

    #DATE CALCULATION UTILITIES

    def get_current_month_year(self):
        """
        Get current month and year.

        Returns:
            Tuple[int, int]: (month, year)
        """
        today = self.get_today()
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

    # === FORMATTING UTILITIES ===

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

    def format_week_display_name(self, week_start, week_end):
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

    # === FILTERING UTILITIES ===

    def filter_events(self, events, filter_criteria):
        """
        Filter a list of events based on multiple criteria.

        Args:
            events (list): List of Event objects to filter
            filter_criteria (dict): Dictionary containing filter options:
                - search_text (str): Text to search in title/description
                - from_date (datetime.date): Start of date range
                - to_date (datetime.date): End of date range
                - show_all_day (bool): Include all-day events
                - show_timed (bool): Include timed events
                - show_recurring (bool): Include recurring events

        Returns:
            list: Filtered list of Event objects
        """
        if not filter_criteria:
            return events

        filtered = []
        search_text = filter_criteria.get('search_text', '').lower()
        from_date = filter_criteria.get('from_date')
        to_date = filter_criteria.get('to_date')
        show_all_day = filter_criteria.get('show_all_day', True)
        show_timed = filter_criteria.get('show_timed', True)
        show_recurring = filter_criteria.get('show_recurring', True)

        for event in events:
            # Text search filter
            if search_text:
                title_match = search_text in event.title.lower()
                desc_match = search_text in event.description.lower()
                if not (title_match or desc_match):
                    continue

            # Date range filter
            if from_date and to_date:
                event_date = datetime.datetime.strptime(event.date, self.DATABASE_DATE_FORMAT).date()
                if not (from_date <= event_date <= to_date):
                    continue

            # Event type filters
            if event.is_all_day and not show_all_day:
                continue
            if not event.is_all_day and not show_timed:
                continue
            if event.is_recurring and not show_recurring:
                continue

            filtered.append(event)

        return filtered