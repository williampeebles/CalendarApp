"""
To Include/Think about
- Let user choose what month it is,
(May implement later, allowing user to see months up to 6-months).

TODOList
-Character limit on description
-When creating an event, if user selects a start day that is after the current date,
then that event should be applied to that selected day
-database
"""

import tkinter as tk
import datetime
import calendar
import random
import tkinter.messagebox as messagebox
from tkcalendar import DateEntry


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

    def add_event(self, event_id, title, date, start_day, end_day, start_time, end_time, description, is_recurring,
                  recurrence_pattern=None):
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
        """
        # create an Event object
        new_event = Event(event_id, title, date, start_day, end_day, start_time, end_time, description, is_recurring,
                          recurrence_pattern)

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

    def update_event(self, event_id, new_title=None, new_start=None, new_end=None, new_desc=None, new_recurring=None, new_recurrence_pattern=None, new_date=None, new_start_day=None, new_end_day=None):
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

    def __init__(self, calendar_obj=None):
        """
        Initialize the MonthViewGUI and create the calendar interface.
        Sets up the main window, creates all GUI components including header,
        month switch button, and calendar grid. Displays the current month
        and starts the tkinter main loop.

        Args:
            calendar_obj (Calendar, optional): Calendar object to manage events
        """
        self.calendar = calendar_obj if calendar_obj else Calendar()
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

    def refresh_calendar_display(self):
        """
        Refresh the calendar display to show updated event highlighting.
        This method is called when events are added, modified, or deleted
        to ensure the calendar buttons reflect the current state of events.
        """
        if self.showing_next:
            if self.current_month < 12:
                year, month = self.current_year, self.current_month + 1
            else:
                year, month = self.current_year + 1, 1
        else:
            year, month = self.current_year, self.current_month
        self.show_month(year, month)

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

    def on_day_click(self, year, month, day):
        """
        Handle when a day button is clicked.

        Opens the DayViewGUI for the selected date if it's current or future date.
        Shows a warning for past dates.

        Args:
            year (int): Year of the clicked date
            month (int): Month of the clicked date
            day (int): Day of the clicked date
        """
        try:
            clicked_date = datetime.date(year, month, day)

            # Check if the date is current or future
            if clicked_date >= datetime.date.today():
                # Open day view for valid dates
                DayViewGUI(self.calendar, year, month, day, parent_gui=self)
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
                    # Determine background color based on event existence
                    date_str = f"{year}-{month:02d}-{day_num:02d}"
                    bg_color = "yellow" if date_str in self.calendar.events_by_date else None
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
    def __init__(self, event_id:str, title:str, date:str, start_day, end_day, start_time:str, end_time:str, description:str, is_recurring:bool, recurrence_pattern=None):
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
        self.date = date
        self.start_day = start_day
        self.end_day = end_day
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.is_recurring = is_recurring
        self.recurrence_pattern = recurrence_pattern


class DayViewGUI():
    """
    A GUI class that displays a detailed day view for managing events.

    This class creates a window interface for a specific day where users can
    view, create, edit, and delete events. Only allows interaction with current
    or future dates.

    Attributes:
        calendar (Calendar): Reference to the main calendar object
        selected_date (datetime.date): The date being viewed
        window (tk.Toplevel): The day view window
        events_listbox (tk.Listbox): Listbox displaying events for the day
    """

    def __init__(self, calendar_obj, year, month, day, parent_gui=None):
        """
        Initialize the DayViewGUI for a specific date.

        Args:
            calendar_obj (Calendar): The calendar object containing events
            year (int): Year of the selected date
            month (int): Month of the selected date
            day (int): Day of the selected date
            parent_gui (MonthViewGUI, optional): Reference to parent month view for refreshing
        """
        self.calendar = calendar_obj
        self.selected_date = datetime.date(year, month, day)
        self.parent_gui = parent_gui

        # Check if the date is valid (current or future)
        if self.selected_date < datetime.date.today():
            tk.messagebox.showwarning("Invalid Date", "Cannot view or edit events for past dates.")
            return

        self.create_day_view_window()

    def create_day_view_window(self):
        """Create and setup the day view window with all components."""
        self.window = tk.Toplevel()
        self.window.title(f"Day View - {self.selected_date.strftime('%A, %B %d, %Y')}")
        self.window.geometry("600x500")
        self.window.resizable(True, True)

        # Header
        header_frame = tk.Frame(self.window)
        header_frame.pack(fill="x", padx=10, pady=5)

        header_label = tk.Label(
            header_frame,
            text=f"{self.selected_date.strftime('%A, %B %d, %Y')}",
            font=("Arial", 18, "bold")
        )
        header_label.pack()

        # Events section
        events_frame = tk.LabelFrame(self.window, text="Events for this Day", font=("Arial", 12, "bold"))
        events_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Listbox with scrollbar for events
        listbox_frame = tk.Frame(events_frame)
        listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        self.events_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,
            font=("Arial", 10)
        )
        self.events_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.events_listbox.yview)

        # Buttons frame
        buttons_frame = tk.Frame(self.window)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        # Event management buttons
        add_btn = tk.Button(
            buttons_frame,
            text="Add New Event",
            command=self.add_event_dialog,
            font=("Arial", 10),
            bg="lightgreen"
        )
        add_btn.pack(side="left", padx=5)

        edit_btn = tk.Button(
            buttons_frame,
            text="Edit Selected Event",
            command=self.edit_event_dialog,
            font=("Arial", 10),
            bg="lightblue"
        )
        edit_btn.pack(side="left", padx=5)

        delete_btn = tk.Button(
            buttons_frame,
            text="Delete Selected Event",
            command=self.delete_event,
            font=("Arial", 10),
            bg="lightcoral"
        )
        delete_btn.pack(side="left", padx=5)

        close_btn = tk.Button(
            buttons_frame,
            text="Close",
            command=self.window.destroy,
            font=("Arial", 10)
        )
        close_btn.pack(side="right", padx=5)

        # Load and display events for this day
        self.current_events = []  # Track current events for deletion
        self.refresh_events_list()

    def refresh_events_list(self):
        """Refresh the events listbox with current events for the selected date."""
        self.events_listbox.delete(0, tk.END)

        # Get events for this date
        date_str = self.selected_date.strftime("%Y-%m-%d")
        self.current_events = self.get_events_for_date(date_str)

        if not self.current_events:
            self.events_listbox.insert(tk.END, "No events scheduled for this day")
        else:
            for event in self.current_events:
                # Create detailed event text
                event_text = f"{event.start_time} - {event.end_time}: {event.title}"
                if event.is_recurring:
                    event_text += f" (Repeats {event.recurrence_pattern})"
                if event.start_day != event.end_day:
                    event_text += f" [{event.start_day} to {event.end_day}]"
                self.events_listbox.insert(tk.END, event_text)

    def get_events_for_date(self, date_str):
        """
        Get all events for a specific date from the calendar.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            list: List of Event objects for the specified date
        """
        return self.calendar.get_events_for_date(date_str)

    def toggle_recurrence_options(self, show, recurrence_frame):
        """Show or hide the recurrence options frame."""
        if show:
            recurrence_frame.grid()
        else:
            recurrence_frame.grid_remove()

    def add_event_dialog(self):
        """Open a dialog to create a new event for the selected date."""
        self.event_form_dialog("Add New Event")

    def edit_event_dialog(self):
        """Open a dialog to edit the selected event."""
        selection = self.events_listbox.curselection()
        if not selection:
            tk.messagebox.showwarning("No Selection", "Please select an event to edit.")
            return

        self.event_form_dialog("Edit Event", selection[0])

    def event_form_dialog(self, title, event_index=None):
        """
        Create a form dialog for adding or editing events.

        Args:
            title (str): Title of the dialog window
            event_index (int, optional): Index of event to edit (None for new event)
        """
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry("500x600")
        dialog.resizable(False, False)

        # Make dialog modal
        dialog.transient(self.window)
        dialog.grab_set()

        # Event form fields
        fields_frame = tk.Frame(dialog)
        fields_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Title field
        tk.Label(fields_frame, text="Event Title:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w",
                                                                                     pady=5)
        title_entry = tk.Entry(fields_frame, font=("Arial", 10), width=30)
        title_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5, sticky="w")

        # Start Date field
        tk.Label(fields_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        start_date_entry = DateEntry(fields_frame, font=("Arial", 10), width=12,
                                   background='darkblue', foreground='white',
                                   borderwidth=2, date_pattern='yyyy-mm-dd',
                                   mindate=datetime.date.today())
        start_date_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        start_date_entry.set_date(self.selected_date)

        # End Date field
        tk.Label(fields_frame, text="End Date:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        end_date_entry = DateEntry(fields_frame, font=("Arial", 10), width=12,
                                 background='darkblue', foreground='white',
                                 borderwidth=2, date_pattern='yyyy-mm-dd',
                                 mindate=datetime.date.today())
        end_date_entry.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        end_date_entry.set_date(self.selected_date)

        # Start time field
        tk.Label(fields_frame, text="Start Time:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        start_time_entry = tk.Entry(fields_frame, font=("Arial", 10), width=15)
        start_time_entry.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        start_time_entry.insert(0, "09:00 AM")

        # End time field
        tk.Label(fields_frame, text="End Time:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        end_time_entry = tk.Entry(fields_frame, font=("Arial", 10), width=15)
        end_time_entry.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        end_time_entry.insert(0, "10:00 AM")

        # Description field
        tk.Label(fields_frame, text="Description:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="nw",
                                                                                     pady=5)
        description_text = tk.Text(fields_frame, font=("Arial", 10), width=30, height=4)
        description_text.grid(row=5, column=1, columnspan=2, pady=5, padx=5, sticky="w")

        # Recurring checkbox
        recurring_var = tk.BooleanVar()
        recurring_check = tk.Checkbutton(
            fields_frame,
            text="Recurring Event",
            variable=recurring_var,
            font=("Arial", 10),
            command=lambda: self.toggle_recurrence_options(recurring_var.get(), recurrence_frame)
        )
        recurring_check.grid(row=6, column=1, sticky="w", pady=5)

        # Recurrence options frame (initially hidden)
        recurrence_frame = tk.LabelFrame(fields_frame, text="Recurrence Options", font=("Arial", 9, "bold"))
        recurrence_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
        recurrence_frame.grid_remove()  # Hide initially

        # Recurrence pattern selection
        tk.Label(recurrence_frame, text="Repeat every:", font=("Arial", 9)).grid(row=0, column=0, sticky="w", padx=5,
                                                                                 pady=2)

        recurrence_var = tk.StringVar(value="weekly")
        recurrence_options = [
            ("Daily", "daily"),
            ("Weekly", "weekly"),
            ("Monthly", "monthly"),
            ("Yearly", "yearly")
        ]

        for i, (text, value) in enumerate(recurrence_options):
            tk.Radiobutton(
                recurrence_frame,
                text=text,
                variable=recurrence_var,
                value=value,
                font=("Arial", 9)
            ).grid(row=1, column=i, sticky="w", padx=5, pady=2)

        # Populate form with existing event data if editing
        if event_index is not None and self.current_events:
            existing_event = self.current_events[event_index]
            title_entry.insert(0, existing_event.title)

            # Parse and set start/end dates
            try:
                start_date_obj = datetime.datetime.strptime(existing_event.start_day, "%Y-%m-%d").date()
                end_date_obj = datetime.datetime.strptime(existing_event.end_day, "%Y-%m-%d").date()
                start_date_entry.set_date(start_date_obj)
                end_date_entry.set_date(end_date_obj)
            except ValueError:
                # Fallback to selected date if parsing fails
                pass

            start_time_entry.delete(0, tk.END)
            start_time_entry.insert(0, existing_event.start_time)

            end_time_entry.delete(0, tk.END)
            end_time_entry.insert(0, existing_event.end_time)

            description_text.insert("1.0", existing_event.description)

            recurring_var.set(existing_event.is_recurring)
            if existing_event.is_recurring and existing_event.recurrence_pattern:
                recurrence_var.set(existing_event.recurrence_pattern)
                self.toggle_recurrence_options(True, recurrence_frame)

        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=10)

        def save_event():
            """Save the event (add new or update existing)."""
            title_text = title_entry.get().strip()
            start_date_obj = start_date_entry.get_date()
            end_date_obj = end_date_entry.get_date()
            start_time = start_time_entry.get().strip()
            end_time = end_time_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            is_recurring = recurring_var.get()
            recurrence_pattern = recurrence_var.get() if is_recurring else None

            # Validation
            if not title_text:
                tk.messagebox.showerror("Error", "Event title is required.")
                return

            if not start_time or not end_time:
                tk.messagebox.showerror("Error", "Start and end times are required.")
                return

            # Validate dates
            try:
                if end_date_obj < start_date_obj:
                    tk.messagebox.showerror("Error", "End date cannot be before start date.")
                    return

                # Convert date objects to strings for storage
                start_date = start_date_obj.strftime("%Y-%m-%d")
                end_date = end_date_obj.strftime("%Y-%m-%d")

            except ValueError:
                tk.messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD format.")
                return

            if title_text and start_date and end_date and start_time and end_time:
                # Update existing event
                if event_index is not None:
                    selected_event = self.current_events[event_index]

                    # Update event in calendar
                    self.calendar.update_event(
                        selected_event.event_id,
                        new_title=title_text,
                        new_start=start_time,
                        new_end=end_time,
                        new_desc=description,
                        new_recurring=is_recurring,
                        new_recurrence_pattern=recurrence_pattern,
                        new_date=start_date,  # Use start_date as the new date
                        new_start_day=start_date,  # Assuming start_day is the same as start_date
                        new_end_day=end_date  # Assuming end_day is the same as end_date
                    )
                else:
                    # New event, generate unique ID
                    event_id = str(random.randint(1000, 1100))

                    # Add event to calendar
                    self.calendar.add_event(
                        event_id, title_text, self.selected_date.strftime("%Y-%m-%d"),
                        start_date, end_date, start_time, end_time, description,
                        is_recurring, recurrence_pattern
                    )

                # Refresh the events list and close dialog
                self.refresh_events_list()
                # Refresh the parent calendar display if available
                if self.parent_gui:
                    self.parent_gui.refresh_calendar_display()
                dialog.destroy()

        save_btn = tk.Button(
            button_frame,
            text="Save Event",
            command=save_event,
            font=("Arial", 10),
            bg="lightgreen"
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            font=("Arial", 10)
        )
        cancel_btn.pack(side="right", padx=5)

    def delete_event(self):
        """Delete the selected event after confirmation."""
        selection = self.events_listbox.curselection()
        if not selection:
            tk.messagebox.showwarning("No Selection", "Please select an event to delete.")
            return

        selected_index = selection[0]

        # Check if there are actual events (not just "No events" message)
        if not self.current_events or selected_index >= len(self.current_events):
            tk.messagebox.showwarning("No Event", "No valid event selected to delete.")
            return

        selected_event = self.current_events[selected_index]

        # Confirm deletion
        confirm = tk.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the event '{selected_event.title}'?"
        )

        if confirm:
            # Delete the event from the calendar
            success = self.calendar.delete_event(selected_event.event_id)

            if success:
                self.refresh_events_list()
                # Refresh the parent calendar display if available
                if self.parent_gui:
                    self.parent_gui.refresh_calendar_display()
                tk.messagebox.showinfo("Success", "Event deleted successfully.")
            else:
                tk.messagebox.showerror("Error", "Failed to delete event.")


# Create a calendar instance and start the GUI
calendar_app = Calendar()
MonthViewGUI(calendar_app)


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