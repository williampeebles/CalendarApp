"""
Calendar Service

This file contains the core calendar logic shared across the application.
It coordinates between the database and the rest of the application.

The service handles:
- Core event operations (create, update, delete)
- Event validation
- Recurring event management
- Event object conversion
- Filter delegation

View-specific operations have been moved to dedicated service classes:
- MonthViewService: Month-specific operations
- WeekViewService: Week-specific operations
- DayViewService: Day-specific operations
- AgendaViewService: Agenda-specific operations

"""

import datetime
import calendar
from Calendar_Database_Class import CalendarDatabase
from Event_Class import Event
from Filter_Service_Class import FilterService



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
        
        # Initialize FilterService with the correct date format
        self.filter_service = FilterService(database_date_format=self.DATABASE_DATE_FORMAT)
        
        # Automatically clean up past events
        self.delete_past_events()

    def _dict_to_event(self, event_dict):
        """
        Convert a database dictionary to an Event object.
        Now delegates to Event class factory method.

        Args:
            event_dict (dict): Dictionary containing event data from database

        Returns:
            Event: Event object created from the dictionary
        """
        # Event class is responsible for creating Event objects
        return Event.from_dict(event_dict)

    def create_event(self,
                     title,
                     date,
                     start_time="",
                     end_time="",
                     description="",
                     is_all_day=False,
                     is_recurring=False,
                     recurrence_pattern="",
                     end_date=None):
        """
        Create a new event with validation.
        If recurring, automatically creates instances for the next 6 months.
        If end_date is different from date, event spans multiple days.

        Args:
            title (str): Event title (required)
            date (datetime.date): Event start date (required)
            start_time (str): Start time (optional for all-day events)
            end_time (str): End time (optional for all-day events)
            description (str): Event description (optional)
            is_all_day (bool): Whether this is an all-day event
            is_recurring (bool): Whether this event repeats
            recurrence_pattern (str): How the event repeats (if recurring)
            end_date (datetime.date): Event end date (optional, defaults to start date)

        Returns:
            Tuple[bool, str, Optional[int]]: (success, message, event_id)
                - success: True if event created successfully
                - message: Success or error message
                - event_id: ID of created event (None if failed)
        """
        # Validate the input data
        is_valid, error_message = self._validate_event_data(
            title, date, start_time, end_time, is_all_day, description
        )

        if not is_valid:
            return False, error_message, None

        try:
            # Convert dates to string format for database storage
            date_str = date.strftime(self.DATABASE_DATE_FORMAT)
            # If no end_date provided, use start date (single-day event)
            if end_date is None:
                end_date = date
            end_date_str = end_date.strftime(self.DATABASE_DATE_FORMAT)

            # Handle all-day events
            if is_all_day:
                start_time = "All Day"
                end_time = "All Day"

            # If recurring, create multiple event instances
            if is_recurring and recurrence_pattern:
                event_ids = self._create_recurring_events(
                    title, date, start_time, end_time, 
                    description, is_all_day, recurrence_pattern
                )
                if event_ids:
                    return True, f"Recurring event created with {len(event_ids)} instances!", event_ids[0]
                else:
                    return False, "Failed to create recurring events", None
            else:
                # Create single event (may span multiple days)
                event_data = {
                    'title': title,
                    'date': date_str,
                    'start_day': date_str,
                    'end_day': end_date_str,
                    'start_time': start_time,
                    'end_time': end_time,
                    'description': description,
                    'is_recurring': False,
                    'recurrence_pattern': None,
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

    def _create_recurring_events(self, title, start_date, start_time, end_time,
                                 description, is_all_day, recurrence_pattern,
                                 num_occurrences=26):
        """
        Create multiple event instances based on recurrence pattern.

        Args:
            title (str): Event title
            start_date (datetime.date): First occurrence date
            start_time (str): Event start time
            end_time (str): Event end time
            description (str): Event description
            is_all_day (bool): Whether it's an all-day event
            recurrence_pattern (str): 'daily', 'weekly', 'monthly', or 'yearly'
            num_occurrences (int): Number of instances to create (default 26 weeks/6 months)

        Returns:
            list: List of created event IDs
        """
        event_ids = []
        current_date = start_date

        for i in range(num_occurrences):
            date_str = current_date.strftime(self.DATABASE_DATE_FORMAT)
            
            event_data = {
                'title': title,
                'date': date_str,
                'start_day': date_str,
                'end_day': date_str,
                'start_time': start_time,
                'end_time': end_time,
                'description': description,
                'is_recurring': True,
                'recurrence_pattern': recurrence_pattern,
                'is_all_day': is_all_day
            }

            try:
                event_id = self.repository.insert_event(event_data)
                event_ids.append(event_id)
            except Exception as e:
                print(f"Warning: Failed to create occurrence on {date_str}: {e}")

            # Calculate next occurrence date
            if recurrence_pattern == 'daily':
                current_date += datetime.timedelta(days=1)
            elif recurrence_pattern == 'weekly':
                current_date += datetime.timedelta(weeks=1)
            elif recurrence_pattern == 'monthly':
                # Add one month (handle month/year boundaries)
                month = current_date.month
                year = current_date.year
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                # Handle day overflow (e.g., Jan 31 -> Feb 28)
                try:
                    current_date = current_date.replace(year=year, month=month)
                except ValueError:
                    # Day doesn't exist in target month, use last day of month
                    last_day = calendar.monthrange(year, month)[1]
                    current_date = current_date.replace(year=year, month=month, day=last_day)
            elif recurrence_pattern == 'yearly':
                # Add one year
                try:
                    current_date = current_date.replace(year=current_date.year + 1)
                except ValueError:
                    # Handle Feb 29 on non-leap years
                    current_date = current_date.replace(year=current_date.year + 1, day=28)

        return event_ids



    def  update_event(self,
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
            event_dict['is_all_day'], event_dict.get('description', '')
        )

        if not is_valid:
            return False, error_message

        # Save the updated event
        try:
            self.repository.update_event(event_dict)
            return True, "Event updated successfully!"
        except Exception as e:
            return False, f"Failed to update event: {str(e)}"

    def delete_event(self, event_id, delete_all_recurring=False):
        """
        Delete an event. If it's a recurring event, can optionally delete all instances.

        Args:
            event_id (int): ID of the event to delete
            delete_all_recurring (bool): If True and event is recurring, delete all instances

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Check if event is recurring
            event_dict = self.repository.get_event_by_id(event_id)
            if not event_dict:
                return False, "Event not found"

            if event_dict['is_recurring'] and delete_all_recurring:
                # Delete all instances of this recurring event
                deleted_count = self.repository.delete_recurring_instances(
                    event_dict['title'],
                    event_dict['recurrence_pattern'],
                    event_dict['date']
                )
                return True, f"Deleted {deleted_count} recurring event instances!"
            else:
                # Delete single event
                self.repository.delete_event(event_id)
                return True, "Event deleted successfully!"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Failed to delete event: {str(e)}"

    def get_recurring_instances(self, event_id):
        """
        Get all instances of a recurring event.

        Args:
            event_id (int): ID of any instance of the recurring event

        Returns:
            List[Event]: All instances of the recurring event, or empty list
        """
        try:
            event_dict = self.repository.get_event_by_id(event_id)
            if not event_dict or not event_dict['is_recurring']:
                return []

            instance_dicts = self.repository.get_recurring_instances(
                event_dict['title'],
                event_dict['recurrence_pattern'],
                event_dict['date']
            )
            return [self._dict_to_event(d) for d in instance_dicts]
        except Exception as e:
            print(f"Error getting recurring instances: {e}")
            return []

    def _validate_event_data(self,
                             title,
                             date,
                             start_time,
                             end_time,
                             is_all_day,
                             description=""):
        """
        Validate event data before creating or updating.

        Args:
            title (str): Event title
            date (datetime.date): Event date
            start_time (str): Start time
            end_time (str): End time
            is_all_day (bool): Whether it's all-day
            description (str, optional): Event description

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Check title
        if not title or not title.strip():
            return False, "Event title is required and cannot be empty"

        # Check description length (80 character limit)
        if description and len(description) > 80:
            return False, f"Description must be 80 characters or less (currently {len(description)} characters)"

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

    def delete_past_events(self):
        """
        Delete all events with dates that have passed (before today).
        This is automatically called when CalendarService is initialized.
        
        Returns:
            int: Number of events deleted
        """
        today = self.get_today()
        today_str = today.strftime(self.DATABASE_DATE_FORMAT)
        
        # Get events from past months (going back 12 months to catch any past events)
        deleted_count = 0
        for month_offset in range(-12, 0):  # Check 12 months back
            target_year = today.year
            target_month = today.month + month_offset
            
            # Adjust for year boundaries
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            # Get events for this past month
            event_dicts = self.repository.get_events_for_month(target_year, target_month)
            
            for event_dict in event_dicts:
                # Check if the event's end date is before today
                end_day_str = event_dict.get('end_day', event_dict.get('date'))
                if end_day_str and end_day_str < today_str:
                    # Event has completely passed, delete it
                    event_id = event_dict.get('event_id')
                    if event_id:
                        self.repository.delete_event(event_id)
                        deleted_count += 1
        
        # Also check current month for any past events
        event_dicts = self.repository.get_events_for_month(today.year, today.month)
        for event_dict in event_dicts:
            end_day_str = event_dict.get('end_day', event_dict.get('date'))
            if end_day_str and end_day_str < today_str:
                event_id = event_dict.get('event_id')
                if event_id:
                    self.repository.delete_event(event_id)
                    deleted_count += 1
        
        return deleted_count

    # === FILTERING UTILITIES ===

    def filter_events(self, events, filter_criteria):
        """
        Filter a list of events based on multiple criteria.
        
        Delegates to FilterService for the actual filtering logic.

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
        return self.filter_service.filter_events(events, filter_criteria)