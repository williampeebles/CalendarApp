import sqlite3


class CalendarDatabase:
    """
    Calendar Database Manager Class

    Handles all database operations for the calendar application including
    creating tables, managing connections, and performing CRUD operations.
    Stores month-specific calendar objects in the database using simple text storage.
    """

    def __init__(self, db_name='calendar.db'):
        """
        Initialize the CalendarDatabase with a database name.

        Args:
            db_name (str): Name of the SQLite database file. Defaults to 'calendar.db'
        """
        self.db_name = db_name
        self.create_database()

    def get_connection(self):
        """
        Create and return a database connection.

        Returns:
            sqlite3.Connection: Database connection object
        """
        return sqlite3.connect(self.db_name)

    def create_database(self):
        """
        Create SQLite database with calendar and event tables.

        Creates a database file with tables for:
        - month_calendars: stores month-specific calendar metadata
        - events: stores event details
        """
        # Create database connection
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create month_calendars table to store calendar metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS month_calendars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month_key TEXT UNIQUE NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create events table with all event data stored directly
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calendar_id INTEGER,
                event_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                start_day TEXT,
                end_day TEXT,
                start_time TEXT,
                end_time TEXT,
                is_all_day BOOLEAN DEFAULT 0,
                recurrence_pattern TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (calendar_id) REFERENCES month_calendars (id)
            )
        ''')

        # Commit changes and close connection
        conn.commit()
        conn.close()

        print("Calendar database created successfully!")
        print(f"Database file: {self.db_name}")
        print("Tables created: month_calendars, events")

    def save_month_calendar(self, month_calendar):
        """
        Save a MonthCalendar object to the database.

        Args:
            month_calendar: MonthCalendar object to save

        Returns:
            int: The database ID of the saved calendar
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        month_key = month_calendar.get_calendar_key()

        # Insert or update the calendar metadata
        cursor.execute('''
            INSERT OR REPLACE INTO month_calendars 
            (month_key, year, month, modified_date)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (month_key, month_calendar.year, month_calendar.month))

        # Get the calendar ID
        cursor.execute('SELECT id FROM month_calendars WHERE month_key = ?', (month_key,))
        calendar_id = cursor.fetchone()[0]

        # Save individual events
        self._save_events_for_calendar(cursor, calendar_id, month_calendar)

        conn.commit()
        conn.close()

        return calendar_id

    def _save_events_for_calendar(self, cursor, calendar_id, month_calendar):
        """
        Save individual events for a calendar to the events table.
        Only saves events that don't already exist to prevent duplicates.

        Args:
            cursor: Database cursor
            calendar_id (int): ID of the calendar in the database
            month_calendar: MonthCalendar object containing events
        """
        # Get existing event IDs for this calendar
        cursor.execute('SELECT event_id FROM events WHERE calendar_id = ?', (calendar_id,))
        existing_event_ids = {row[0] for row in cursor.fetchall()}

        # Insert only new events
        for event_id, event in month_calendar.calendar.events.items():
            if event_id not in existing_event_ids:
                cursor.execute('''
                    INSERT INTO events 
                    (calendar_id, event_id, title, description, date, start_day, end_day,
                     start_time, end_time, is_all_day, recurrence_pattern)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    calendar_id, event_id, event.title, event.description, event.date,
                    event.start_day, event.end_day, event.start_time, event.end_time,
                    event.is_all_day, event.recurrence_pattern
                ))

    def load_month_calendar(self, year, month):
        """
        Load calendar data from the database for a specific month.

        Args:
            year (int): Year of the calendar
            month (int): Month of the calendar

        Returns:
            dict or None: Calendar data with events and events_by_date if found, None otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        month_key = f"{year}-{month:02d}"

        # Get calendar ID
        cursor.execute('SELECT id FROM month_calendars WHERE month_key = ?', (month_key,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return None

        calendar_id = result[0]

        # Get all events for this calendar
        cursor.execute('''
            SELECT event_id, title, description, date, start_day, end_day,
                   start_time, end_time, is_all_day, recurrence_pattern
            FROM events WHERE calendar_id = ?
        ''', (calendar_id,))

        events_data = cursor.fetchall()
        conn.close()

        # Reconstruct events dictionary and events_by_date
        events = {}
        events_by_date = {}

        for event_data in events_data:
            event_id, title, description, date, start_day, end_day, start_time, end_time, is_all_day, recurrence_pattern = event_data

            # Create a simple event object (dict) with the data
            event_dict = {
                'event_id': event_id,
                'title': title,
                'description': description,
                'date': date,
                'start_day': start_day,
                'end_day': end_day,
                'start_time': start_time,
                'end_time': end_time,
                'is_all_day': bool(is_all_day),
                'is_recurring': bool(recurrence_pattern is not None and recurrence_pattern.strip()),
                'recurrence_pattern': recurrence_pattern
            }

            events[event_id] = event_dict

            # Add to events_by_date
            if date not in events_by_date:
                events_by_date[date] = []
            events_by_date[date].append(event_id)

        return {
            'events': events,
            'events_by_date': events_by_date
        }

    def get_all_month_calendars(self):
        """
        Get information about all stored month calendars.

        Returns:
            list: List of tuples (month_key, year, month, created_date)
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT month_key, year, month, created_date 
            FROM month_calendars 
            ORDER BY year, month
        ''')

        results = cursor.fetchall()
        conn.close()

        return results

    def save_single_event(self, calendar_id, event):
        """
        Save a single event to the database.

        Args:
            calendar_id (int): ID of the calendar in the database
            event: Event object to save
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if event already exists
        cursor.execute('SELECT id FROM events WHERE calendar_id = ? AND event_id = ?',
                       (calendar_id, event.event_id))
        existing = cursor.fetchone()

        if existing:
            # Update existing event
            cursor.execute('''
                UPDATE events SET
                title = ?, description = ?, date = ?, start_day = ?, end_day = ?,
                start_time = ?, end_time = ?, is_all_day = ?, recurrence_pattern = ?,
                modified_date = CURRENT_TIMESTAMP
                WHERE calendar_id = ? AND event_id = ?
            ''', (
                event.title, event.description, event.date, event.start_day, event.end_day,
                event.start_time, event.end_time, event.is_all_day, event.recurrence_pattern,
                calendar_id, event.event_id
            ))
        else:
            # Insert new event
            cursor.execute('''
                INSERT INTO events 
                (calendar_id, event_id, title, description, date, start_day, end_day,
                 start_time, end_time, is_all_day, recurrence_pattern)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                calendar_id, event.event_id, event.title, event.description, event.date,
                event.start_day, event.end_day, event.start_time, event.end_time,
                event.is_all_day, event.recurrence_pattern
            ))

        conn.commit()
        conn.close()

    def delete_single_event(self, calendar_id, event_id):
        """
        Delete a single event from the database.

        Args:
            calendar_id (int): ID of the calendar in the database
            event_id (str): ID of the event to delete

        Returns:
            bool: True if deleted, False if not found
        """
        print(f"DEBUG: delete_single_event called with calendar_id={calendar_id}, event_id={event_id}")

        conn = self.get_connection()
        cursor = conn.cursor()

        # First check if the event exists
        cursor.execute('SELECT * FROM events WHERE calendar_id = ? AND event_id = ?',
                       (calendar_id, event_id))
        existing = cursor.fetchone()
        print(f"DEBUG: Found existing event: {existing}")

        cursor.execute('DELETE FROM events WHERE calendar_id = ? AND event_id = ?',
                       (calendar_id, event_id))

        deleted = cursor.rowcount > 0
        print(f"DEBUG: Deletion affected {cursor.rowcount} rows")

        conn.commit()
        conn.close()

        return deleted

    def delete_month_calendar(self, year, month):
        """
        Delete a month calendar from the database.

        Args:
            year (int): Year of the calendar to delete
            month (int): Month of the calendar to delete

        Returns:
            bool: True if deleted, False if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        month_key = f"{year}-{month:02d}"

        # Delete the calendar (events will be deleted by foreign key constraint)
        cursor.execute('DELETE FROM month_calendars WHERE month_key = ?', (month_key,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def close_connection(self, conn):
        """
        Close a database connection.
        Args:
            conn (sqlite3.Connection): Database connection to close
        """
        if conn:
            conn.close()


# Initialize the database
if __name__ == "__main__":
    calendar_db = CalendarDatabase()