import Calendar_Class

class MonthCalendar:
    """
    A calendar class that represents a specific month.
    Each instance manages events for a single month and year.
    Integrates with database for persistent storage.
    """

    def __init__(self, year, month, db_manager=None):
        """
        Initialize a calendar for a specific month and year.

        Args:
            year (int): The year for this calendar
            month (int): The month for this calendar (1-12)
            db_manager (CalendarDatabase, optional): Database manager for persistence
        """
        self.year = year
        self.month = month
        self.db_manager = db_manager
        self.calendar = Calendar_Class.Calendar()

        # Load existing data from database if available
        if self.db_manager:
            self._load_from_database()

    def _load_from_database(self):
        """Load calendar data from the database."""
        try:
            calendar_data = self.db_manager.load_month_calendar(self.year, self.month)
            if calendar_data:
                # Convert dictionary events back to Event objects
                import Event_Class

                for event_id, event_dict in calendar_data.get('events', {}).items():
                    # Create Event object from dictionary data
                    event_obj = Event_Class.Event(
                        event_dict['event_id'],
                        event_dict['title'],
                        event_dict['date'],
                        event_dict['start_day'],
                        event_dict['end_day'],
                        event_dict['start_time'],
                        event_dict['end_time'],
                        event_dict['description'],
                        event_dict['is_recurring'],
                        event_dict['recurrence_pattern'],
                        event_dict.get('is_all_day', False)  # Default to False if not present
                    )
                    self.calendar.events[event_id] = event_obj

                self.calendar.events_by_date = calendar_data.get('events_by_date', {})

                print(f"Loaded calendar data for {self.get_calendar_key()}")

            # Always update the next_event_id counter based on ALL events in the database
            # This ensures we don't reuse event IDs across different months
            if self.db_manager:
                max_id = self.db_manager.get_max_event_id()
                self.calendar.next_event_id = max_id + 1
                print(f"Set next_event_id to {self.calendar.next_event_id} based on global max ID {max_id}")
            else:
                # If no database manager, check local events only (fallback)
                if self.calendar.events:
                    max_id = 0
                    for event_id in self.calendar.events.keys():
                        try:
                            numeric_id = int(event_id)
                            max_id = max(max_id, numeric_id)
                        except ValueError:
                            pass
                    self.calendar.next_event_id = max_id + 1
        except Exception as e:
            print(f"Error loading calendar data: {e}")

    def _save_to_database(self):
        """Save calendar data to the database."""
        if self.db_manager:
            try:
                self.db_manager.save_month_calendar(self)
                print(f"Saved calendar data for {self.get_calendar_key()}")
            except Exception as e:
                print(f"Error saving calendar data: {e}")

    def get_calendar_key(self):
        """
        Get a unique key for this month calendar.

        Returns:
            str: Key in format "YYYY-MM"
        """
        return f"{self.year}-{self.month:02d}"

    def add_event(self, *args, **kwargs):
        """Delegate event addition to the underlying calendar and save individual event to database."""
        result = self.calendar.add_event(*args, **kwargs)
        # Save only the new event instead of the entire calendar
        if result is None and args:  # If add_event succeeded and we have an event_id
            event_id = args[0]  # First argument is event_id
            event = self.calendar.get_event(event_id)
            if event and self.db_manager:
                try:
                    # Ensure the month calendar exists in database first
                    calendar_id = self._ensure_calendar_in_database()
                    self.db_manager.save_single_event(calendar_id, event)
                    print(f"Saved individual event {event_id} to database")
                except Exception as e:
                    print(f"Error saving individual event: {e}")
        return result

    def get_event(self, *args, **kwargs):
        """Delegate event retrieval to the underlying calendar."""
        return self.calendar.get_event(*args, **kwargs)

    def get_events_for_date(self, *args, **kwargs):
        """Delegate event retrieval by date to the underlying calendar."""
        return self.calendar.get_events_for_date(*args, **kwargs)

    def update_event(self, *args, **kwargs):
        """Delegate event updating to the underlying calendar and save individual event to database."""
        result = self.calendar.update_event(*args, **kwargs)
        # Save only the updated event
        if result and args:  # If update_event succeeded and we have an event_id
            event_id = args[0]  # First argument is event_id
            event = self.calendar.get_event(event_id)
            if event and self.db_manager:
                try:
                    calendar_id = self._ensure_calendar_in_database()
                    self.db_manager.save_single_event(calendar_id, event)
                    print(f"Updated individual event {event_id} in database")
                except Exception as e:
                    print(f"Error updating individual event: {e}")
        return result

    def delete_event(self, *args, **kwargs):
        """Delegate event deletion to the underlying calendar and remove from database."""
        print(f"DEBUG: delete_event called with args={args}, kwargs={kwargs}")

        # First delete from the calendar
        result = self.calendar.delete_event(*args, **kwargs)
        print(f"DEBUG: Calendar deletion result: {result}")

        # Only delete from database if calendar deletion was successful
        if result and args:  # If deletion succeeded and we have an event_id
            event_id = args[0]  # First argument is event_id
            print(f"DEBUG: Attempting to delete event_id {event_id} from database")

            if self.db_manager:
                try:
                    calendar_id = self._ensure_calendar_in_database()
                    print(f"DEBUG: Got calendar_id: {calendar_id}")

                    if calendar_id:
                        db_deleted = self.db_manager.delete_single_event(calendar_id, event_id)
                        print(f"DEBUG: Database deletion result: {db_deleted}")
                        if db_deleted:
                            print(f"Deleted individual event {event_id} from database")
                        else:
                            print(f"Event {event_id} was not found in database")
                    else:
                        print("DEBUG: calendar_id is None, cannot delete from database")
                except Exception as e:
                    print(f"Error deleting individual event from database: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("DEBUG: No db_manager available")
        else:
            print(f"DEBUG: Not deleting from database - result={result}, args={args}")

        return result

    def _get_calendar_id(self):
        """Get the database ID for this month calendar."""
        if not self.db_manager:
            print("DEBUG: No db_manager in _get_calendar_id")
            return None

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()

        month_key = self.get_calendar_key()
        print(f"DEBUG: Looking for calendar with month_key: {month_key}")
        cursor.execute('SELECT id FROM month_calendars WHERE month_key = ?', (month_key,))
        result = cursor.fetchone()
        print(f"DEBUG: Calendar query result: {result}")

        conn.close()

        return result[0] if result else None

    def _ensure_calendar_in_database(self):
        """Ensure the month calendar exists in database and return its ID."""
        if not self.db_manager:
            return None

        # First try to get existing ID
        calendar_id = self._get_calendar_id()

        if calendar_id is None:
            # Calendar doesn't exist, create it
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()

            month_key = self.get_calendar_key()
            cursor.execute('''
                INSERT OR REPLACE INTO month_calendars 
                (month_key, year, month, modified_date)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (month_key, self.year, self.month))

            # Get the ID of the created calendar
            cursor.execute('SELECT id FROM month_calendars WHERE month_key = ?', (month_key,))
            calendar_id = cursor.fetchone()[0]

            conn.commit()
            conn.close()

            print(f"DEBUG: Created new calendar in database with ID: {calendar_id}")

    @property
    def events_by_date(self):
        """Access the events_by_date from the underlying calendar."""
        return self.calendar.events_by_date
