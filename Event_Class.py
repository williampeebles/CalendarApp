class Event(object):
    """
    Represents a calendar event with all its properties.
    This class stores information about a single calendar event including
    timing details, description, and recurrence status.
    Attributes:
        event_id (str): Unique identifier for the event
        title (str): The title/name of the event
        date (str): The date of the event
        start_day (str): The starting date of the event in YYYY-MM-DD format
        end_day (str): The ending date of the event in YYYY-MM-DD format
        start_time (str): The start time of the event
        end_time (str): The end time of the event
        description (str): Detailed description of the event
        is_recurring (bool): Whether the event repeats regularly
        recurrence_pattern (str): How often the event repeats (daily, weekly, monthly, yearly)
        is_all_day (bool): Whether the event is an all-day event
    """
    def __init__(self, event_id:str, title:str, date:str, start_day, end_day, start_time:str, end_time:str, description:str, is_recurring:bool, recurrence_pattern=None, is_all_day:bool=False):
        """
        Initialize an Event object with all necessary properties.
        Args:
            event_id (str): Unique identifier for the event
            title (str): The title/name of the event
            date (str): The date when the event occurs
            start_day: The starting day of the event
            end_day: The ending day of the event
            start_time (str): The time when the event starts
            end_time (str): The time when the event ends
            description (str): Detailed description of what the event is about
            is_recurring (bool): True if the event repeats, False for one-time events
            recurrence_pattern (str, optional): How often the event repeats (e.g., "daily", "weekly", "monthly", "yearly")
            is_all_day (bool, optional): True if the event is an all-day event, False for timed events
        """
        self._event_id = event_id
        self._title = title
        self._date = date
        self._start_day = start_day
        self._end_day = end_day
        self._start_time = start_time
        self._end_time = end_time
        self._description = description
        self._is_recurring = is_recurring
        self._recurrence_pattern = recurrence_pattern
        self._is_all_day = is_all_day

    # Event ID property
    @property
    def event_id(self):
        """Get the event ID."""
        return self._event_id

    @event_id.setter
    def event_id(self, value):
        """Set the event ID."""
        if not isinstance(value, str):
            raise TypeError("Event ID must be a string")
        if not value.strip():
            raise ValueError("Event ID cannot be empty")
        self._event_id = value

    # Title property
    @property
    def title(self):
        """Get the event title."""
        return self._title

    @title.setter
    def title(self, value):
        """Set the event title."""
        if not isinstance(value, str):
            raise TypeError("Title must be a string")
        if not value.strip():
            raise ValueError("Title cannot be empty")
        self._title = value

    # Date property
    @property
    def date(self):
        """Get the event date."""
        return self._date

    @date.setter
    def date(self, value):
        """Set the event date."""
        if not isinstance(value, str):
            raise TypeError("Date must be a string")
        if not value.strip():
            raise ValueError("Date cannot be empty")
        self._date = value

    # Start day property
    @property
    def start_day(self):
        """Get the start day."""
        return self._start_day

    @start_day.setter
    def start_day(self, value):
        """Set the start day."""
        self._start_day = value

    # End day property
    @property
    def end_day(self):
        """Get the end day."""
        return self._end_day

    @end_day.setter
    def end_day(self, value):
        """Set the end day."""
        self._end_day = value

    # Start time property
    @property
    def start_time(self):
        """Get the start time."""
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        """Set the start time."""
        if not isinstance(value, str):
            raise TypeError("Start time must be a string")
        self._start_time = value

    # End time property
    @property
    def end_time(self):
        """Get the end time."""
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        """Set the end time."""
        if not isinstance(value, str):
            raise TypeError("End time must be a string")
        self._end_time = value

    # Description property
    @property
    def description(self):
        """Get the event description."""
        return self._description

    @description.setter
    def description(self, value):
        """Set the event description."""
        if not isinstance(value, str):
            raise TypeError("Description must be a string")
        self._description = value

    # Is recurring property
    @property
    def is_recurring(self):
        """Get whether the event is recurring."""
        return self._is_recurring

    @is_recurring.setter
    def is_recurring(self, value):
        """Set whether the event is recurring."""
        if not isinstance(value, bool):
            raise TypeError("is_recurring must be a boolean")
        self._is_recurring = value

    # Recurrence pattern property
    @property
    def recurrence_pattern(self):
        """Get the recurrence pattern."""
        return self._recurrence_pattern

    @recurrence_pattern.setter
    def recurrence_pattern(self, value):
        """Set the recurrence pattern."""
        if value is not None and not isinstance(value, str):
            raise TypeError("Recurrence pattern must be a string or None")
        self._recurrence_pattern = value

    # Is all day property
    @property
    def is_all_day(self):
        """Get whether the event is all day."""
        return self._is_all_day

    @is_all_day.setter
    def is_all_day(self, value):
        """Set whether the event is all day."""
        if not isinstance(value, bool):
            raise TypeError("is_all_day must be a boolean")
        self._is_all_day = value