import datetime
from Event_Class import Event


class Calendar(object):
    """
    A Calendar class that manages events and calendar functionality.
    This class handles the storage and management of events, including adding,
    updating, deleting, and retrieving events. It maintains the current date
    and month information.
    Attributes:
        current_month (int): The current month as an integer (1-12)
        current_date (datetime.date): Today's date
        events (dict): Dictionary storing events with event_id as keys and dates as values
    """

    def __init__(self):
        """
        Initialize the Calendar with current date information and empty events dictionary.
        Sets up the calendar with today's date, current month, and an empty events
        dictionary to store future events.
        """
        self.current_month = datetime.date.today().month
        self.current_date = datetime.date.today()
        self.events = {}  # Dictionary: {event_id: Event_object}
        self.events_by_date = {}  # Dictionary: {date_string: [event_ids]}
        self.next_event_id = 1  # Counter for sequential event IDs

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

    def update_event(self, event_id, new_title=None, new_start=None, new_end=None, new_desc=None, new_recurring=None, new_recurrence_pattern=None, new_date=None, new_start_day=None, new_end_day=None, new_all_day=None):
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