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
import calendar


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
        # For in-memory databases, keep a persistent connection
        self._persistent_conn = None
        if db_name == ':memory:':
            self._persistent_conn = sqlite3.connect(db_name)
        self._create_tables()

    def _create_tables(self):
        """
        Create the database tables if they don't exist yet.
        This is called automatically when the repository is created.
        """
        with self._get_connection() as conn:
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

    def _get_connection(self):
        """
        Create and return a database connection.

        Returns:
            sqlite3.Connection: Database connection object
        """
        # Use persistent connection for in-memory databases
        if self._persistent_conn:
            return self._persistent_conn
        return sqlite3.connect(self.db_name)

    def _row_to_dict(self, row):
        """
        Convert a database row into a dictionary.

        Args:
            row: Database row with event data

        Returns:
            dict: Dictionary with event data
        """
        event_id, title, description, date, start_day, end_day, start_time, end_time, is_all_day, is_recurring, recurrence_pattern = row[:11]

        return {
            'event_id': event_id,
            'title': title,
            'description': description,
            'date': date,
            'start_day': start_day,
            'end_day': end_day,
            'start_time': start_time,
            'end_time': end_time,
            'is_all_day': bool(is_all_day),
            'is_recurring': bool(is_recurring),
            'recurrence_pattern': recurrence_pattern
        }

    def insert_event(self, event_data):
        """
        Insert a new event into the database.

        Args:
            event_data (dict): Dictionary containing event data

        Returns:
            int: The auto-generated event_id

        Raises:
            Exception: If insert fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events 
                (title, description, date, start_day, end_day, 
                 start_time, end_time, is_all_day, is_recurring, recurrence_pattern)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event_data['title'],
                event_data.get('description', ''),
                event_data['date'],
                event_data['start_day'],
                event_data['end_day'],
                event_data['start_time'],
                event_data['end_time'],
                event_data.get('is_all_day', False),
                event_data.get('is_recurring', False),
                event_data.get('recurrence_pattern')
            ))
            event_id = cursor.lastrowid
            conn.commit()
            return event_id

    def get_event_by_id(self, event_id):
        """
        Get a specific event by its ID.

        Args:
            event_id (int): The ID of the event to find

        Returns:
            dict or None: Event data dictionary if found, None otherwise

        Raises:
            Exception: If query fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT event_id, title, description, date, start_day, end_day,
                       start_time, end_time, is_all_day, is_recurring, recurrence_pattern
                FROM events WHERE event_id = ?
            ''', (event_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_dict(row)
            return None

    def get_events_for_month(self, year, month):
        """
        Get all events for a specific month and year.
        Includes multi-day events that start or end in this month.

        Args:
            year (int): The year (e.g., 2025)
            month (int): The month (1-12)

        Returns:
            List[dict]: List of event dictionaries for that month

        Raises:
            Exception: If query fails
        """
        
        
        # Calculate first and last day of month
        first_day = f"{year}-{month:02d}-01"
        last_day = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]:02d}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Get events that start in month OR span into month
            cursor.execute('''
                SELECT event_id, title, description, date, start_day, end_day,
                       start_time, end_time, is_all_day, is_recurring, recurrence_pattern
                FROM events 
                WHERE (date >= ? AND date <= ?)
                   OR (start_day <= ? AND end_day >= ?)
                ORDER BY date, start_time
            ''', (first_day, last_day, last_day, first_day))
            
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_events_for_date(self, date_str):
        """
        Get all events for a specific date.
        Includes multi-day events that span across this date.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            List[dict]: List of event dictionaries for that date

        Raises:
            Exception: If query fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Get events that start on this date OR span across it
            cursor.execute('''
                SELECT event_id, title, description, date, start_day, end_day,
                       start_time, end_time, is_all_day, is_recurring, recurrence_pattern
                FROM events 
                WHERE ? BETWEEN start_day AND end_day
                ORDER BY start_time
            ''', (date_str,))
            
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def update_event(self, event_data):
        """
        Update an existing event in the database.

        Args:
            event_data (dict): Dictionary containing event data with event_id

        Returns:
            bool: True if successful

        Raises:
            ValueError: If event_id not provided
            Exception: If update fails
        """
        if 'event_id' not in event_data:
            raise ValueError("event_id is required for update")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE events SET 
                title = ?, description = ?, date = ?, start_day = ?, end_day = ?,
                start_time = ?, end_time = ?, is_all_day = ?, is_recurring = ?, 
                recurrence_pattern = ?, modified_date = CURRENT_TIMESTAMP
                WHERE event_id = ?
            ''', (
                event_data['title'],
                event_data.get('description', ''),
                event_data['date'],
                event_data['start_day'],
                event_data['end_day'],
                event_data['start_time'],
                event_data['end_time'],
                event_data.get('is_all_day', False),
                event_data.get('is_recurring', False),
                event_data.get('recurrence_pattern'),
                event_data['event_id']
            ))
            conn.commit()
            return True

    def delete_event(self, event_id):
        """
        Delete an event from the database.

        Args:
            event_id (int): The ID of the event to delete

        Returns:
            bool: True if deleted successfully

        Raises:
            ValueError: If event_id does not exist
            Exception: If delete fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM events WHERE event_id = ?', (event_id,))
            rows_deleted = cursor.rowcount > 0
            conn.commit()
            
            if not rows_deleted:
                raise ValueError(f"Event with id {event_id} not found")
            
            return True