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
        self.event_id = event_id
        self.title = title
        self.date = date
        self.start_day = start_day
        self.end_day = end_day
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.is_recurring = is_recurring
        self.recurrence_pattern = recurrence_pattern
        self.is_all_day = is_all_day