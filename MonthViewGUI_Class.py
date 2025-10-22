import tkinter as tk
import datetime
import calendar
import tkinter.messagebox as messagebox
import Calendar_Class
import DayViewGUI_Class
import Calendar_Database_Class


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
                        event_dict['recurrence_pattern']
                    )
                    self.calendar.events[event_id] = event_obj

                self.calendar.events_by_date = calendar_data.get('events_by_date', {})
                print(f"Loaded calendar data for {self.get_calendar_key()}")
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
        """Delegate event addition to the underlying calendar and save to database."""
        result = self.calendar.add_event(*args, **kwargs)
        self._save_to_database()
        return result

    def get_event(self, *args, **kwargs):
        """Delegate event retrieval to the underlying calendar."""
        return self.calendar.get_event(*args, **kwargs)

    def get_events_for_date(self, *args, **kwargs):
        """Delegate event retrieval by date to the underlying calendar."""
        return self.calendar.get_events_for_date(*args, **kwargs)

    def update_event(self, *args, **kwargs):
        """Delegate event updating to the underlying calendar and save to database."""
        result = self.calendar.update_event(*args, **kwargs)
        self._save_to_database()
        return result

    def delete_event(self, *args, **kwargs):
        """Delegate event deletion to the underlying calendar and save to database."""
        result = self.calendar.delete_event(*args, **kwargs)
        self._save_to_database()
        return result

    @property
    def events_by_date(self):
        """Access the events_by_date from the underlying calendar."""
        return self.calendar.events_by_date


class MonthViewGUI():
    """
    A GUI class that displays a monthly calendar view using tkinter.
    This class creates a graphical calendar interface that shows a month view
    with clickable day buttons, navigation between months, and proper highlighting
    of today's date. Each month uses its own calendar object for event management.

    Attributes:
        window (tk.Tk): Main tkinter window
        today (datetime.date): Today's date for highlighting
        current_month (int): Current month being displayed
        current_year (int): Current year being displayed
        showing_next (bool): Flag to track if showing current or next month
        header (tk.Label): Label displaying the month and year
        switch_btn (tk.Button): Button to switch between current and next month
        frame (tk.Frame): Frame containing the calendar grid
        month_calendars (dict): Dictionary storing MonthCalendar objects by month key
        current_calendar (MonthCalendar): Currently active month calendar
    """

    def __init__(self, calendar_obj=None):
        """
        Initialize the MonthViewGUI and create the calendar interface.
        Sets up the main window, creates all GUI components including header,
        month switch button, and calendar grid. Displays the current month
        and starts the tkinter main loop.

        Args:
            calendar_obj (Calendar, optional): Legacy parameter for compatibility
        """
        # Initialize database manager
        self.db_manager = Calendar_Database_Class.CalendarDatabase()
        self.month_calendars = {}  # Dictionary to store month-specific calendars
        self.window = tk.Tk()
        self.window.title("Month View Calendar")
        self.today = datetime.date.today()
        self.current_month = self.today.month
        self.current_year = self.today.year
        self.showing_next = False

        # Initialize the current month calendar
        self.current_calendar = self._get_month_calendar(self.current_year, self.current_month)

        self.header = tk.Label(self.window, font=("Arial", 16, "bold"))
        self.header.grid(row=0, column=0, columnspan=7)

        self.switch_btn = tk.Button(self.window, text="Show Next Month", command=self.switch_month)
        self.switch_btn.grid(row=1, column=0, columnspan=7)

        self.frame = tk.Frame(self.window)
        self.frame.grid(row=2, column=0, columnspan=7)

        # Set up window close protocol to save data
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.show_month(self.current_year, self.current_month)
        self.window.mainloop()

    def on_closing(self):
        """
        Handle window closing event. Save all calendar data before closing.
        """
        try:
            # Save all month calendars to database
            for month_calendar in self.month_calendars.values():
                month_calendar._save_to_database()
            print("All calendar data saved successfully.")
        except Exception as e:
            print(f"Error saving calendar data on exit: {e}")
        finally:
            self.window.destroy()

    def _get_month_calendar(self, year, month):
        """
        Get or create a MonthCalendar object for the specified year and month.
        Loads from database if available, creates new if not.

        Args:
            year (int): The year for the calendar
            month (int): The month for the calendar

        Returns:
            MonthCalendar: The calendar object for the specified month
        """
        month_key = f"{year}-{month:02d}"
        if month_key not in self.month_calendars:
            self.month_calendars[month_key] = MonthCalendar(year, month, self.db_manager)
        return self.month_calendars[month_key]

    def refresh_calendar_display(self):
        """
        Refresh the calendar display to show updated event highlighting.
        This method is called when events are added, modified, or deleted
        to ensure the calendar buttons reflect the current state of events.
        Updates the current calendar reference based on the displayed month.
        """
        if self.showing_next:
            if self.current_month < 12:
                year, month = self.current_year, self.current_month + 1
            else:
                year, month = self.current_year + 1, 1
        else:
            year, month = self.current_year, self.current_month

        # Update the current calendar reference
        self.current_calendar = self._get_month_calendar(year, month)
        self.show_month(year, month)

    def switch_month(self):
        """
        Toggle between current month and next month display.
        Switches the calendar view between the current month and the next month.
        Updates the button text accordingly and refreshes the calendar display.
        Handles year rollover when switching from December to January.
        Updates the current calendar reference to the appropriate month.
        """
        self.showing_next = not self.showing_next
        if self.showing_next:
            if self.current_month < 12:
                year, month = self.current_year, self.current_month + 1
            else:
                year, month = self.current_year + 1, 1
            self.switch_btn.config(text="Show This Month")
        else:
            year, month = self.current_year, self.current_month
            self.switch_btn.config(text="Show Next Month")

        # Update the current calendar reference
        self.current_calendar = self._get_month_calendar(year, month)
        self.show_month(year, month)

    def on_day_click(self, year, month, day):
        """
        Handle when a day button is clicked.

        Opens the DayViewGUI for the selected date if it's current or future date.
        Shows a warning for past dates. Uses the appropriate month calendar for the date.

        Args:
            year (int): Year of the clicked date
            month (int): Month of the clicked date
            day (int): Day of the clicked date
        """
        try:
            clicked_date = datetime.date(year, month, day)

            # Check if the date is current or future
            if clicked_date >= datetime.date.today():
                # Get the calendar for the clicked date's month
                clicked_month_calendar = self._get_month_calendar(year, month)
                # Open day view for valid dates with the correct month calendar
                DayViewGUI_Class.DayViewGUI(clicked_month_calendar, year, month, day, parent_gui=self)
            else:
                # Show warning for past dates
                messagebox.showwarning(
                    "Invalid Date",
                    "Cannot view or edit events for past dates."
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_month(self, year, month):
        """
        Display a specific month and year in the calendar grid.
        Clears the existing calendar display and creates a new grid showing
        the specified month. Creates day-of-week headers, calculates proper
        positioning for days, and highlights today's date if it's in the
        displayed month. Uses the appropriate month calendar for event highlighting.

        Args:
            year (int): The year to display
            month (int): The month to display (1-12)
        """
        # Get the calendar for this specific month
        month_calendar = self._get_month_calendar(year, month)

        for widget in self.frame.winfo_children():
            widget.destroy()
        self.header.config(text=f"{calendar.month_name[month]} {year}")

        days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        col = 0
        while col < 7:
            tk.Button(self.frame, text=days_of_the_week[col], width=15, height=2, state="disabled").grid(row=0,
                                                                                                         column=col)
            col += 1

        first_weekday, num_days = calendar.monthrange(year, month)
        # Adjust so Sunday is column 0
        start_col = (first_weekday + 1) % 7

        # Fill the entire calendar grid (6 rows x 7 columns)
        row = 1
        day_num = 1

        for week in range(6):  # 6 weeks maximum
            for col in range(7):  # 7 days per week
                current_pos = week * 7 + col

                # Check if we're before the first day of the month
                if current_pos < start_col:
                    # Empty button for days before the month starts
                    tk.Button(self.frame, text="", width=15, height=7, state="disabled").grid(row=row, column=col)

                # Check if we're within the days of the current month
                elif day_num <= num_days:
                    if (year, month, day_num) == (self.today.year, self.today.month, self.today.day):
                        fg = "red"
                    else:
                        fg = "black"
                    # Determine background color based on event existence in this month's calendar
                    date_str = f"{year}-{month:02d}-{day_num:02d}"
                    bg_color = "yellow" if date_str in month_calendar.events_by_date else None
                    # Create clickable day button
                    day_button = tk.Button(
                        self.frame,
                        text=day_num,
                        anchor="ne",
                        width=15,
                        height=7,
                        fg=fg,
                        bg=bg_color,
                        command=lambda y=year, m=month, d=day_num: self.on_day_click(y, m, d)
                    )
                    day_button.grid(row=row, column=col)
                    day_num += 1

                # Empty button for days after the month ends
                else:
                    tk.Button(self.frame, text="", width=15, height=7, state="disabled").grid(row=row, column=col)

            row += 1
            # Stop creating rows if we've placed all days and filled the current row
            if day_num > num_days and col == 6:
                break
