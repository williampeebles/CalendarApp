import tkinter as tk
import datetime
import calendar
import tkinter.messagebox as messagebox
import DayViewGUI_Class


class WeekViewGUI:
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
        calendar_obj (Calendar): Calendar object for event management
        parent_gui (MonthViewGUI): Reference to parent month view for data consistency
    """

    def __init__(self, calendar_obj, year, month, day, parent_gui=None):
        """
        Initialize the WeekViewGUI for a specific date's week.

        Args:
            calendar_obj (Calendar): The calendar object containing events
            year (int): Year of the selected date
            month (int): Month of the selected date
            day (int): Day of the selected date
            parent_gui (MonthViewGUI, optional): Reference to parent month view for refreshing
        """
        # Store the calendar object for all operations
        self.calendar = calendar_obj
        self.selected_date = datetime.date(year, month, day)
        self.parent_gui = parent_gui

        # Get today from service
        self.today = self.calendar.get_today()

        # Calculate the start of the week using service
        self.current_week_start = self.calendar.calculate_week_start(self.selected_date)

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

    def next_week(self):
        """Navigate to the next week."""
        self.current_week_start += datetime.timedelta(days=7)
        self.show_week()

    def go_to_current_week(self):
        """Navigate to the current week containing today's date."""
        today = self.calendar.get_today()
        self.current_week_start = self.calendar.calculate_week_start(today)
        self.show_week()

    def on_day_click(self, date):
        """
        Handle when a day button is clicked.

        Opens the DayViewGUI for the selected date if it's current or future date.
        Shows a warning for past dates.

        Args:
            date (datetime.date): The clicked date
        """
        try:
            # Check if the date is current or future using service
            if date >= self.calendar.get_today():
                # Open day view for valid dates - pass self as parent for refresh callback
                DayViewGUI_Class.DayViewGUI(self.calendar, date.year, date.month, date.day, parent_gui=self)
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

        # Use service for week display formatting
        header_text = self.calendar.format_week_display_name(self.current_week_start, week_end)
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

            # Check for events using the new calendar system
            has_events = self.calendar.has_events_on_date(current_date)
            bg_color = "yellow" if has_events else None

            # Create button text with date and day
            button_text = f"{current_date.day}\n{calendar.month_name[current_date.month][:3]}"

            # Add event count if there are events
            if has_events:
                events_on_date = self.calendar.get_events_for_date(current_date)
                event_count = len(events_on_date)
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

    def refresh_calendar_display(self):
        """
        Compatibility method for DayViewGUI parent refresh calls.
        Refreshes both the week display and the parent month view if available.
        """
        self.show_week()
        if self.parent_gui:
            self.parent_gui.refresh_calendar_display()