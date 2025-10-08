"""
To Include/Think about

- Let user choose what month it is
- Specify what a whole month is - Done
- The object should include a list of events
- Click on day then display a list of events
- Buttons for calendar days
- Start day, end Day
- Use calendar class to store data

TODOList
"""

import tkinter as tk
import datetime
import calendar
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
        self.current_day = datetime.date.today()
        self.current_month = self.current_day.month
        self.events = {} # title as the keys, and the values as the dates


    def add_event(self, event_id, title, date, start_time, end_time, description, is_recurring):
        '''
        Add a new event to the calendar.
        Creates an Event object with the provided details and stores it in the
        events dictionary using the event_id as the key.            Args:
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
        '''
        # create an Event object
        new_event = Event(event_id, title, date, start_time, end_time, description, is_recurring)

        # store it in events dictionary
        self.events[new_event.event_id] = date  # changed dictionary key to event id

    def get_event(self, title):
        """
        Retrieve an event by its event_id.
        Searches the events dictionary for an event with the specified event_id
        and returns it if found.
        Args:
            event_id (str): The event_id of the event to retrieve
        Returns:
            Event or None: The event object if found, None otherwise
        """
        if title in self.events:
            return self.events[title]
        else:
            return None

    def update_event(self, date, event_id, new_title=None, new_start=None, new_end=None, new_desc=None,
                     new_recurring=None):
        """
        Update an existing event's properties.
        Finds an event by date and event_id, then updates any provided properties.
        Only non-None parameters will be updated.
        Args:
            date (str): The date of the event to update
            event_id (str): The unique identifier of the event
            new_title (str, optional): New title for the event
            new_start (str, optional): New start time for the event
            new_end (str, optional): New end time for the event
            new_desc (str, optional): New description for the event
            new_recurring (bool, optional): New recurring status for the event
        """
        if date in self.events:
            for event in self.events[date]:
                if event.event_id == event_id:
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

    def delete_event(self, title):
        """
        Delete an event from the calendar.
        Removes an event from both the events dictionary and events_by_date.
        Args:
            event_id (str): The event_id of the event to delete

        Returns:
            bool: True if event was deleted, False if event not found
        """
        if title in self.events:
            del self.events[title]

    def get_month_view(self):
        """
        Get a month view representation of the calendar.
        This method is intended to return a formatted view of the current month
        showing all events. Currently not implemented.
        Returns:
            None: Method is not yet implemented
        """
        pass

class MonthViewGUI():
    """
    A GUI class that displays a monthly calendar view using tkinter.
    This class creates a graphical calendar interface that shows a month view
    with clickable day buttons, navigation between months, and proper highlighting
    of today's date.
    Attributes:
        window (tk.Tk): Main tkinter window
        today (datetime.date): Today's date for highlighting
        current_month (int): Current month being displayed
        current_year (int): Current year being displayed
        showing_next (bool): Flag to track if showing current or next month
        header (tk.Label): Label displaying the month and year
        switch_btn (tk.Button): Button to switch between current and next month
        frame (tk.Frame): Frame containing the calendar grid
    """
    def __init__(self):
        """
        Initialize the MonthViewGUI and create the calendar interface.
        Sets up the main window, creates all GUI components including header,
        month switch button, and calendar grid. Displays the current month
        and starts the tkinter main loop.

        Args:
            calendar_obj (Calendar, optional): Calendar object to manage events
        """
        self.window = tk.Tk()
        self.window.title("Month View Calendar")
        self.today = datetime.date.today()
        self.current_month = self.today.month
        self.current_year = self.today.year
        self.showing_next = False

        self.header = tk.Label(self.window, font=("Arial", 16, "bold"))
        self.header.grid(row=0, column=0, columnspan=7)

        self.switch_btn = tk.Button(self.window, text="Show Next Month", command=self.switch_month)
        self.switch_btn.grid(row=1, column=0, columnspan=7)

        self.frame = tk.Frame(self.window)
        self.frame.grid(row=2, column=0, columnspan=7)

        self.show_month(self.current_year, self.current_month)
        self.window.mainloop()

    def switch_month(self):
        """
        Toggle between current month and next month display.
        Switches the calendar view between the current month and the next month.
        Updates the button text accordingly and refreshes the calendar display.
        Handles year rollover when switching from December to January.
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
        self.show_month(year, month)

    def show_month(self, year, month):
        """
        Display a specific month and year in the calendar grid.
        Clears the existing calendar display and creates a new grid showing
        the specified month. Creates day-of-week headers, calculates proper
        positioning for days, and highlights today's date if it's in the
        displayed month.
        Args:
            year (int): The year to display
            month (int): The month to display (1-12)
        """
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

                    # Create clickable day button
                    day_button = tk.Button(
                        self.frame,
                        text=day_num,
                        anchor="ne",
                        width=15,
                        height=7,
                        fg=fg,
                        command=lambda d=day_num, m=month, y=year: self.on_day_click(y, m, d)
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
    """
    def __init__(self, event_id:str, title:str, date:str, start_day, end_day, start_time:str, end_time:str, description:str, is_recurring:bool):
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
        """
        self.event_id = event_id
        self.title = title
        self.date = date # Added the date attribute
        self.start_day: start_day #Added start day
        self.end_day: end_day #Added end day
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.is_recurring = is_recurring


MonthViewGUI()


# Added: self.window.title("Month View Calendar") to set the window title.
# Added: self.today = datetime.date.today() to track today's date.
# Added: self.current_month and self.current_year to store the current month and year.
# Added: self.showing_next to track which month is displayed.
# Added: self.header label to display the month and year.
# Added: self.switch_btn button to toggle between current and next month.
# Added: self.frame to contain the calendar grid.
# Replaced: static month display with self.show_month(self.current_year, self.current_month).
# Added: switch_month method to handle toggling between months.
# Added: show_month method to dynamically display the correct month and highlight today's date.
# Changed: Days of the week are displayed using a while loop instead of a for loop.
# Changed: Calculation of the starting column for the first day using col = (first_weekday + 1) % 7 for correct alignment.
# Changed: Day buttons are created in a while loop, with today's date highlighted in red.
# Removed: monthsOfYear dictionary and static button creation for days.
# Removed: static for loops for days and weeks; replaced with dynamic month rendering.