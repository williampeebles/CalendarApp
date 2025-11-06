import datetime
import calendar
from Event_Class import Event
from MonthCalendar_Class import MonthCalendar
import Calendar_Database_Class


class Calendar(object):
    """
    Enhanced Calendar class that manages events, calendar functionality, and logic.
    This ensures GUI classes only handle presentation while all data processing
    happens in this centralized calendar class.
    
    Attributes:
        current_month (int): The current month as an integer (1-12)
        current_date (datetime.date): Today's date
        events (dict): Dictionary storing events with event_id as keys
        events_by_date (dict): Dictionary mapping date strings to event ID lists
        next_event_id (int): Counter for sequential event IDs
        db_manager (CalendarDatabase): Database manager for persistence
        month_calendars (dict): Cache for month calendar instances
    """

    def __init__(self):
        """
        Initialize the Calendar with current date information, database, and caching.
        Sets up the calendar with today's date, current month, empty events
        dictionary, database manager, and month calendar cache.
        """
        self.current_month = datetime.date.today().month
        self.current_date = datetime.date.today()
        self.events = {}  # Dictionary: {event_id: Event_object}
        self.events_by_date = {}  # Dictionary: {date_string: [event_ids]}
        self.next_event_id = 1  # Counter for sequential event IDs
        
        # Service layer attributes
        self.db_manager = Calendar_Database_Class.CalendarDatabase()
        self.month_calendars = {}  # Cache for month calendar instances

    def generate_event_id(self):
        """
        Generate a sequential event ID from 001 to 100.
        Returns:
            str: Event ID in format '001', '002', etc.
        Raises:
            Exception: If all 100 IDs are used
        """
        if self.next_event_id > 100:
            raise Exception("Maximum number of events (100) reached")

        event_id = f"{self.next_event_id:03d}"
        self.next_event_id += 1
        return event_id

    def add_event(self, event_id, title, date, start_day, end_day, start_time, end_time, description, is_recurring,
                  recurrence_pattern=None, is_all_day=False):
        """
        Add a new event to the calendar.
        Creates an Event object with the provided details and stores it in the
        events dictionary using the event_id as the key.
        Args:
            event_id (str): Unique identifier for the event
            title (str): Title/name of the event
            date (str): Date of the event in YYYY-MM-DD format
            start_day (str): Starting date of the event in YYYY-MM-DD format
            end_day (str): Ending date of the event in YYYY-MM-DD format
            start_time (str): Start time of the event
            end_time (str): End time of the event
            description (str): Detailed description of the event
            is_recurring (bool): Whether the event repeats
            recurrence_pattern (str, optional): How often it repeats
            is_all_day (bool, optional): Whether the event is an all-day event
        """
        # create an Event object
        new_event = Event(event_id, title, date, start_day, end_day, start_time, end_time, description, is_recurring,
                          recurrence_pattern, is_all_day)

        # store it in events dictionary
        self.events[event_id] = new_event

        # Also store by date for easy retrieval
        if date not in self.events_by_date:
            self.events_by_date[date] = []
        self.events_by_date[date].append(event_id)

    def get_event(self, event_id):
        """
        Retrieve an event by its event_id.
        Searches the events dictionary for an event with the specified event_id
        and returns it if found.
        Args:
            event_id (str): The event_id of the event to retrieve
        Returns:
            Event or None: The event object if found, None otherwise
        """
        return self.events.get(event_id, None)

    def get_events_for_date(self, date_str):
        """
        Get all events for a specific date.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            list: List of Event objects for the specified date
        """
        event_ids = self.events_by_date.get(date_str, [])
        return [self.events[event_id] for event_id in event_ids if event_id in self.events]

    def update_event(self, event_id, new_title=None, new_start=None, new_end=None, new_desc=None, new_recurring=None,
                     new_recurrence_pattern=None, new_date=None, new_start_day=None, new_end_day=None,
                     new_all_day=None):
        """
        Update an existing event's properties.

        Args:
            event_id (str): The unique identifier of the event
            new_title (str, optional): New title for the event
            new_start (str, optional): New start time for the event
            new_end (str, optional): New end time for the event
            new_desc (str, optional): New description for the event
            new_recurring (bool, optional): New recurring status for the event
            new_recurrence_pattern (str, optional): New recurrence pattern for the event
            new_date (str, optional): New date for the event in YYYY-MM-DD format
            new_start_day (str, optional): New start day in YYYY-MM-DD format
            new_end_day (str, optional): New end day in YYYY-MM-DD format
            new_all_day (bool, optional): New all-day status for the event
        Returns:
            bool: True if event updated, False if event not found
        """
        if event_id in self.events:
            event = self.events[event_id]
            if new_title is not None:
                event.title = new_title
            if new_start is not None:
                event.start_time = new_start
            if new_end is not None:
                event.end_time = new_end
            if new_desc is not None:
                event.description = new_desc
            if new_recurring is not None:
                event.is_recurring = new_recurring
            if new_recurrence_pattern is not None:
                event.recurrence_pattern = new_recurrence_pattern
            if new_date is not None and new_date != event.date:
                old_date = event.date
                event.date = new_date
                if old_date in self.events_by_date and event_id in self.events_by_date[old_date]:
                    self.events_by_date[old_date].remove(event_id)
                    if not self.events_by_date[old_date]:
                        del self.events_by_date[old_date]
                if new_date not in self.events_by_date:
                    self.events_by_date[new_date] = []
                self.events_by_date[new_date].append(event_id)
            if new_start_day is not None:
                event.start_day = new_start_day
            if new_end_day is not None:
                event.end_day = new_end_day
            if new_all_day is not None:
                event.is_all_day = new_all_day
            return True
        return False

    def delete_event(self, event_id):
        """
        Delete an event from the calendar.
        Removes an event from both the events dictionary and events_by_date.
        Args:
            event_id (str): The event_id of the event to delete

        Returns:
            bool: True if event was deleted, False if event not found
        """
        if event_id in self.events:
            event = self.events[event_id]
            date_str = event.date

            # Remove from events dictionary
            del self.events[event_id]

            # Remove from events_by_date
            if date_str in self.events_by_date:
                if event_id in self.events_by_date[date_str]:
                    self.events_by_date[date_str].remove(event_id)
                # Clean up empty date entries
                if not self.events_by_date[date_str]:
                    del self.events_by_date[date_str]

            return True
        return False
    
    def get_today(self):
        """Get today's date."""
        return datetime.date.today()
        
    def get_current_month_year(self):
        """
        Get current month and year.
        
        Returns:
            tuple: (month, year) as integers
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
            tuple: (next_year, next_month) as integers
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
            tuple: (previous_year, previous_month) as integers
        """
        if month > 1:
            return year, month - 1
        else:
            return year - 1, 12
            
    def calculate_week_start(self, date):
        """
        Calculate the start of the week (Sunday) for a given date.
        
        Args:
            date (datetime.date): The date to calculate week start for
            
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
            list: List of 7 datetime.date objects for the week
        """
        return [week_start + datetime.timedelta(days=i) for i in range(7)]
        
    def get_month_calendar(self, year, month):
        """
        Get or create a MonthCalendar for the specified year and month.
        Uses caching to avoid recreating calendars that have already been loaded.
        
        Args:
            year (int): Year for the calendar
            month (int): Month for the calendar (1-12)
            
        Returns:
            MonthCalendar: The calendar object for the specified month
        """
        month_key = f"{year}-{month:02d}"
        if month_key not in self.month_calendars:
            self.month_calendars[month_key] = MonthCalendar(year, month, self.db_manager)
        return self.month_calendars[month_key]
        
    def save_all_calendars(self):
        """Save all cached month calendars to the database."""
        try:
            for month_calendar in self.month_calendars.values():
                month_calendar._save_to_database()
            return True, "All calendar data saved successfully."
        except Exception as e:
            return False, f"Error saving calendar data: {e}"
            
    def validate_date_range(self, start_date, end_date):
        """
        Validate that a date range is valid.
        
        Args:
            start_date (datetime.date): Start date
            end_date (datetime.date): End date
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if end_date < start_date:
            return False, "End date cannot be before start date."
            
        if start_date < datetime.date.today():
            return False, "Cannot create events for past dates."
            
        return True, ""
        
    def validate_event_data(self, title, start_date, end_date, start_time, end_time, is_all_day):
        """
        Validate event data for creation or updating.
        
        Args:
            title (str): Event title
            start_date (datetime.date): Start date
            end_date (datetime.date): End date  
            start_time (str): Start time
            end_time (str): End time
            is_all_day (bool): Whether event is all-day
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate title
        if not title or not title.strip():
            return False, "Event title is required."
            
        # Validate date range
        is_valid, error_msg = self.validate_date_range(start_date, end_date)
        if not is_valid:
            return False, error_msg
            
        # Validate times for non-all-day events
        if not is_all_day:
            if not start_time or not start_time.strip():
                return False, "Start time is required for timed events."
            if not end_time or not end_time.strip():
                return False, "End time is required for timed events."
                
        return True, ""
        
    def format_month_display_name(self, year, month):
        """
        Format month and year for display.
        
        Args:
            year (int): Year
            month (int): Month (1-12)
            
        Returns:
            str: Formatted month name and year (e.g., "November 2024")
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
            
    def create_event(self, month_calendar, title, start_date, end_date, start_time, end_time, description, is_recurring, recurrence_pattern, is_all_day):
        """
        Create a new event with validation and proper data handling.
        
        Args:
            month_calendar (MonthCalendar): Calendar to add event to
            title (str): Event title
            start_date (datetime.date): Start date
            end_date (datetime.date): End date
            start_time (str): Start time
            end_time (str): End time
            description (str): Event description
            is_recurring (bool): Whether event repeats
            recurrence_pattern (str): How event repeats
            is_all_day (bool): Whether event is all-day
            
        Returns:
            tuple: (success, message, event_id)
        """
        # Validate event data
        is_valid, error_msg = self.validate_event_data(title, start_date, end_date, start_time, end_time, is_all_day)
        if not is_valid:
            return False, error_msg, None
            
        try:
            # Generate event ID
            event_id = month_calendar.calendar.generate_event_id()
            
            # Convert dates to strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Handle all-day event times
            if is_all_day:
                start_time = "All Day"
                end_time = "All Day"
                
            # Add event to calendar
            month_calendar.add_event(
                event_id, title, start_date_str, start_date_str, end_date_str,
                start_time, end_time, description, is_recurring, recurrence_pattern, is_all_day
            )
            
            return True, "Event created successfully.", event_id
            
        except Exception as e:
            return False, str(e), None
            
    def update_event_in_calendar(self, month_calendar, event_id, title, start_date, end_date, start_time, end_time, description, is_recurring, recurrence_pattern, is_all_day):
        """
        Update an existing event with validation and proper data handling.
        
        Args:
            month_calendar (MonthCalendar): Calendar containing the event
            event_id (str): ID of event to update
            title (str): New event title
            start_date (datetime.date): New start date
            end_date (datetime.date): New end date
            start_time (str): New start time
            end_time (str): New end time
            description (str): New event description
            is_recurring (bool): New recurring status
            recurrence_pattern (str): New recurrence pattern
            is_all_day (bool): New all-day status
            
        Returns:
            tuple: (success, message)
        """
        # Validate event data
        is_valid, error_msg = self.validate_event_data(title, start_date, end_date, start_time, end_time, is_all_day)
        if not is_valid:
            return False, error_msg
            
        try:
            # Convert dates to strings
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Handle all-day event times
            if is_all_day:
                start_time = "All Day"
                end_time = "All Day"
                
            # Update event in calendar
            success = month_calendar.update_event(
                event_id,
                new_title=title,
                new_start=start_time,
                new_end=end_time,
                new_desc=description,
                new_recurring=is_recurring,
                new_recurrence_pattern=recurrence_pattern,
                new_date=start_date_str,
                new_start_day=start_date_str,
                new_end_day=end_date_str,
                new_all_day=is_all_day
            )
            
            if success:
                return True, "Event updated successfully."
            else:
                return False, "Event not found."
                
        except Exception as e:
            return False, str(e)
            
    def delete_event_from_calendar(self, month_calendar, event_id):
        """
        Delete an event with proper error handling.
        
        Args:
            month_calendar (MonthCalendar): Calendar containing the event
            event_id (str): ID of event to delete
            
        Returns:
            tuple: (success, message)
        """
        try:
            success = month_calendar.delete_event(event_id)
            if success:
                return True, "Event deleted successfully."
            else:
                return False, "Event not found."
        except Exception as e:
            return False, str(e)
            
    def get_events_for_date_obj(self, month_calendar, date):
        """
        Get all events for a specific date.
        
        Args:
            month_calendar (MonthCalendar): Calendar to search
            date (datetime.date): Date to get events for
            
        Returns:
            list: List of Event objects for the date
        """
        date_str = date.strftime("%Y-%m-%d")
        return month_calendar.get_events_for_date(date_str)
        
    def get_all_events(self, month_calendar):
        """
        Get all events from a calendar across all dates.
        
        Args:
            month_calendar (MonthCalendar): Calendar to get events from
            
        Returns:
            list: List of all Event objects in the calendar
        """
        # Handle different calendar object types
        if hasattr(month_calendar, 'calendar') and hasattr(month_calendar.calendar, 'events'):
            # This is a MonthCalendar object
            calendar_obj = month_calendar.calendar
        elif hasattr(month_calendar, 'events'):
            # This is a Calendar object directly
            calendar_obj = month_calendar
        else:
            return []
            
        if calendar_obj.events:
            return list(calendar_obj.events.values())
        else:
            return []
            
    def has_events_on_date(self, month_calendar, date):
        """
        Check if there are any events on a specific date.
        
        Args:
            month_calendar (MonthCalendar): Calendar to check
            date (datetime.date): Date to check
            
        Returns:
            bool: True if there are events on the date, False otherwise
        """
        date_str = date.strftime("%Y-%m-%d")
        return date_str in month_calendar.events_by_date
        
    def format_date_for_display(self, date):
        """
        Format a date for user display.
        
        Args:
            date (datetime.date): Date to format
            
        Returns:
            str: Formatted date string
        """
        return date.strftime("%A, %B %d, %Y")
        
    def parse_date_string(self, date_str):
        """
        Parse a date string into a datetime.date object.
        
        Args:
            date_str (str): Date string in YYYY-MM-DD format
            
        Returns:
            tuple: (success, date_object_or_error_message)
        """
        try:
            return True, datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD format."