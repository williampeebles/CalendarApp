import tkinter as tk
import datetime
import calendar
import tkinter.messagebox as messagebox
import DayViewGUI_Class


class WeekViewGUI():
    """
    A GUI class that displays a weekly calendar view using tkinter.
    This class creates a graphical calendar interface that shows a week view
    with clickable day buttons, navigation between weeks, and proper highlighting
    of today's date. Integrates with the existing calendar system for event management.

    Attributes:
        window (tk.Toplevel): Week view window
        today (datetime.date): Today's date for highlighting
        current_week_start (datetime.date): Start date of the currently displayed week
        header (tk.Label): Label displaying the week range
        frame (tk.Frame): Frame containing the week grid
        calendar_obj (MonthCalendar): Calendar object for event management
        parent_gui (MonthViewGUI): Reference to parent month view for data consistency
    """

    def __init__(self, calendar_obj, year, month, day, parent_gui=None):
        """
        Initialize the WeekViewGUI for a specific date's week.

        Args:
            calendar_obj (MonthCalendar): The calendar object containing events
            year (int): Year of the selected date
            month (int): Month of the selected date
            day (int): Day of the selected date
            parent_gui (MonthViewGUI, optional): Reference to parent month view for refreshing
        """
        self.calendar_obj = calendar_obj
        self.selected_date = datetime.date(year, month, day)
        self.parent_gui = parent_gui
        self.today = datetime.date.today()

        # Calculate the start of the week (Sunday)
        days_since_sunday = (self.selected_date.weekday() + 1) % 7
        self.current_week_start = self.selected_date - datetime.timedelta(days=days_since_sunday)

        self.create_week_view_window()

    def create_week_view_window(self):
        """Create and setup the week view window with all components."""
        self.window = tk.Toplevel()
        self.window.title("Week View Calendar")
        self.window.geometry("800x400")
        self.window.resizable(True, True)

        # Header showing week range
        self.header = tk.Label(self.window, font=("Arial", 16, "bold"))
        self.header.grid(row=0, column=0, columnspan=7, pady=10)

        # Navigation buttons
        nav_frame = tk.Frame(self.window)
        nav_frame.grid(row=1, column=0, columnspan=7, pady=5)

        prev_btn = tk.Button(nav_frame, text="Previous Week", command=self.previous_week)
        prev_btn.pack(side=tk.LEFT, padx=10)

        next_btn = tk.Button(nav_frame, text="Next Week", command=self.next_week)
        next_btn.pack(side=tk.RIGHT, padx=10)

        today_btn = tk.Button(nav_frame, text="This Week", command=self.go_to_current_week)
        today_btn.pack(side=tk.LEFT, padx=10)

        # Frame for the week grid
        self.frame = tk.Frame(self.window)
        self.frame.grid(row=2, column=0, columnspan=7, padx=10, pady=10)

        self.show_week()

        # Set window close protocol
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Handle window closing event."""
        self.window.destroy()

    def previous_week(self):
        """Navigate to the previous week."""
        self.current_week_start -= datetime.timedelta(days=7)
        self.show_week()

    def next_week(self):
        """Navigate to the next week."""
        self.current_week_start += datetime.timedelta(days=7)
        self.show_week()

    def go_to_current_week(self):
        """Navigate to the current week containing today's date."""
        days_since_sunday = (self.today.weekday() + 1) % 7
        self.current_week_start = self.today - datetime.timedelta(days=days_since_sunday)
        self.show_week()

    def get_calendar_for_date(self, date):
        """
        Get the appropriate calendar object for a specific date.
        Uses the parent GUI's method to get the correct month calendar.

        Args:
            date (datetime.date): The date to get the calendar for

        Returns:
            MonthCalendar: The calendar object for the date's month
        """
        if self.parent_gui:
            return self.parent_gui._get_month_calendar(date.year, date.month)
        return self.calendar_obj

    def on_day_click(self, date):
        """
        Handle when a day button is clicked.

        Opens the DayViewGUI for the selected date if it's current or future date.
        Shows a warning for past dates.

        Args:
            date (datetime.date): The clicked date
        """
        try:
            # Check if the date is current or future
            if date >= datetime.date.today():
                # Get the appropriate calendar for the clicked date
                date_calendar = self.get_calendar_for_date(date)
                # Open day view for valid dates - pass self as parent for refresh callback
                DayViewGUI_Class.DayViewGUI(date_calendar, date.year, date.month, date.day, parent_gui=self)
            else:
                # Show warning for past dates
                messagebox.showwarning(
                    "Invalid Date",
                    "Cannot view or edit events for past dates."
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_week(self):
        """
        Display the current week in the calendar grid.
        Creates a 7-day horizontal layout with day buttons showing date info
        and event indicators.
        """
        # Clear existing widgets
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Calculate week end date for header
        week_end = self.current_week_start + datetime.timedelta(days=6)

        # Update header with week range
        if self.current_week_start.year == week_end.year:
            if self.current_week_start.month == week_end.month:
                header_text = f"{calendar.month_name[self.current_week_start.month]} {self.current_week_start.day}-{week_end.day}, {self.current_week_start.year}"
            else:
                header_text = f"{calendar.month_name[self.current_week_start.month]} {self.current_week_start.day} - {calendar.month_name[week_end.month]} {week_end.day}, {self.current_week_start.year}"
        else:
            header_text = f"{calendar.month_name[self.current_week_start.month]} {self.current_week_start.day}, {self.current_week_start.year} - {calendar.month_name[week_end.month]} {week_end.day}, {week_end.year}"

        self.header.config(text=header_text)

        # Days of the week headers
        days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        for col in range(7):
            # Day of week header
            day_header = tk.Label(self.frame, text=days_of_the_week[col], font=("Arial", 12, "bold"))
            day_header.grid(row=0, column=col, padx=2, pady=2)

        # Create day buttons for the week
        for col in range(7):
            current_date = self.current_week_start + datetime.timedelta(days=col)

            # Determine text color (red for today)
            if current_date == self.today:
                fg = "red"
            else:
                fg = "black"

            # Get the appropriate calendar for this date
            date_calendar = self.get_calendar_for_date(current_date)

            # Determine background color based on event existence
            date_str = f"{current_date.year}-{current_date.month:02d}-{current_date.day:02d}"
            has_events = date_str in date_calendar.events_by_date
            bg_color = "yellow" if has_events else None

            # Create button text with date and day
            button_text = f"{current_date.day}\n{calendar.month_name[current_date.month][:3]}"

            # Add event count if there are events
            if has_events:
                event_count = len(date_calendar.events_by_date[date_str])
                button_text += f"\n({event_count} event{'s' if event_count != 1 else ''})"

            # Create clickable day button
            day_button = tk.Button(
                self.frame,
                text=button_text,
                width=15,
                height=8,
                fg=fg,
                bg=bg_color,
                command=lambda d=current_date: self.on_day_click(d),
                font=("Arial", 10)
            )
            day_button.grid(row=1, column=col, padx=2, pady=2, sticky="nsew")

        # Configure column weights for responsive layout
        for col in range(7):
            self.frame.columnconfigure(col, weight=1)

    def refresh_week_display(self):
        """
        Refresh the week display to show updated event highlighting.
        This method should be called when events are added, modified, or deleted
        to ensure the week buttons reflect the current state of events.
        """
        self.show_week()

    def refresh_calendar_display(self):
        """
        Compatibility method for DayViewGUI parent refresh calls.
        Refreshes both the week display and the parent month view if available.
        """
        self.refresh_week_display()
        if self.parent_gui:
            self.parent_gui.refresh_calendar_display()