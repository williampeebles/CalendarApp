"""
Calendar Database Class

This file contains the actual database operations using SQLite.
It implements the EventRepository interface, meaning it MUST have all the methods
defined in EventRepository.py.

This class handles:
- Creating database tables
- Saving events to the database
- Loading events from the database
- Updating and deleting events
"""

import sqlite3
from Event_Class import Event


class CalendarDatabase:
    """
    Concrete implementation of EventRepository using SQLite database.

    This class does the actual work of storing and retrieving events from
    a SQLite database file.
    """

    def __init__(self, db_name: str = 'calendar.db'):
        """
        Initialize the database connection and create tables if needed.

        Args:
            db_name (str): Name of the database file to use
        """
        self.db_name = db_name
        self._create_tables()

    def _create_tables(self):
        """
        Create the database tables if they don't exist yet.
        This is called automatically when the repository is created.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create events table - this stores all our event data
        # event_id is now auto-incrementing primary key, just like CalendarDatabase
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                start_day TEXT,
                end_day TEXT,
                start_time TEXT,
                end_time TEXT,
                is_all_day BOOLEAN DEFAULT 0,
                is_recurring BOOLEAN DEFAULT 0,
                recurrence_pattern TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def _get_connection(self):
        """
        Create and return a database connection.

        Returns:
            sqlite3.Connection: Database connection object
        """
        return sqlite3.connect(self.db_name)

    def _event_from_row(self, row):
        """
        Convert a database row into an Event object.

        Args:
            row: Database row with event data

        Returns:
            Event: Event object created from the row data
        """
        event_id, title, description, date, start_day, end_day, start_time, end_time, is_all_day, is_recurring, recurrence_pattern = row[
                                                                                                                                     :11]

        return Event(
            event_id=event_id,
            title=title,
            date=date,
            start_day=start_day,
            end_day=end_day,
            start_time=start_time,
            end_time=end_time,
            description=description,
            is_recurring=bool(is_recurring),
            recurrence_pattern=recurrence_pattern,
            is_all_day=bool(is_all_day)
        )

    def save_event(self, event):
        """
        Save a single event to the database.

        Args:
            event (Event): The event to save

        Returns:
            int: The event_id of the saved event (0 if failed)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if hasattr(event, 'event_id') and event.event_id and str(event.event_id).isdigit():
                # Update existing event
                cursor.execute('''
                    UPDATE events SET 
                    title = ?, description = ?, date = ?, start_day = ?, end_day = ?,
                    start_time = ?, end_time = ?, is_all_day = ?, is_recurring = ?, 
                    recurrence_pattern = ?, modified_date = CURRENT_TIMESTAMP
                    WHERE event_id = ?
                ''', (
                    event.title, event.description, event.date, event.start_day, event.end_day,
                    event.start_time, event.end_time, event.is_all_day, event.is_recurring,
                    event.recurrence_pattern, event.event_id
                ))
                event_id = int(event.event_id)
            else:
                # Insert new event (let database auto-generate the ID)
                cursor.execute('''
                    INSERT INTO events 
                    (title, description, date, start_day, end_day, 
                     start_time, end_time, is_all_day, is_recurring, recurrence_pattern)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.title, event.description, event.date, event.start_day, event.end_day,
                    event.start_time, event.end_time, event.is_all_day, event.is_recurring,
                    event.recurrence_pattern
                ))
                event_id = cursor.lastrowid  # Get the auto-generated ID

            conn.commit()
            conn.close()
            return event_id

        except Exception as e:
            print(f"Error saving event: {e}")
            return 0

    def get_event_by_id(self, event_id):
        """
        Get a specific event by its ID.

        Args:
            event_id (int): The ID of the event to find

        Returns:
            Event or None: The event if found, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT event_id, title, description, date, start_day, end_day,
                       start_time, end_time, is_all_day, is_recurring, recurrence_pattern
                FROM events WHERE event_id = ?
            ''', (event_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return self._event_from_row(row)
            return None

        except Exception as e:
            print(f"Error getting event by ID: {e}")
            return None

    def get_events_for_month(self, year, month):
        """
        Get all events for a specific month and year.

        Args:
            year (int): The year (e.g., 2025)
            month (int): The month (1-12)

        Returns:
            List[Event]: List of events in that month
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create date pattern for the month (e.g., "2025-11%" for November 2025)
            month_pattern = f"{year}-{month:02d}%"

            cursor.execute('''
                SELECT event_id, title, description, date, start_day, end_day,
                       start_time, end_time, is_all_day, is_recurring, recurrence_pattern
                FROM events WHERE date LIKE ?
                ORDER BY date, start_time
            ''', (month_pattern,))

            rows = cursor.fetchall()
            conn.close()

            # Convert all rows to Event objects
            events = []
            for row in rows:
                events.append(self._event_from_row(row))

            return events

        except Exception as e:
            print(f"Error getting events for month: {e}")
            return []

    def get_events_for_date(self, date_str):
        """
        Get all events for a specific date.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            List[Event]: List of events on that date
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT event_id, title, description, date, start_day, end_day,
                       start_time, end_time, is_all_day, is_recurring, recurrence_pattern
                FROM events WHERE date = ?
                ORDER BY start_time
            ''', (date_str,))

            rows = cursor.fetchall()
            conn.close()

            # Convert all rows to Event objects
            events = []
            for row in rows:
                events.append(self._event_from_row(row))

            return events

        except Exception as e:
            print(f"Error getting events for date: {e}")
            return []

    def update_event(self, event):
        """
        Update an existing event.

        Args:
            event (Event): The event with updated information

        Returns:
            bool: True if updated successfully, False otherwise
        """
        # For SQLite with INSERT OR REPLACE, this is the same as save_event
        return self.save_event(event)

    def delete_event(self, event_id):
        """
        Delete an event from the database.

        Args:
            event_id (int): The ID of the event to delete

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM events WHERE event_id = ?', (event_id,))

            # Check if any row was actually deleted
            rows_deleted = cursor.rowcount > 0

            conn.commit()
            conn.close()

            return rows_deleted

        except Exception as e:
            print(f"Error deleting event: {e}")
            return False

