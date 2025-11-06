import tkinter as tk
import Calendar_Class
import DayViewGUI_Class
import WeekViewGUI_Class
import AgendaViewGUI_Class
import datetime
import calendar
from tkinter import messagebox


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
            calendar_obj (Calendar, optional): Calendar object for data operations
        """
        # Use provided calendar or create a new one
        self.calendar = calendar_obj if calendar_obj else Calendar_Class.Calendar()
        self.window = tk.Tk()
        self.window.title("Month View Calendar")
        
        # Get current date from calendar
        today = self.calendar.get_today()
        self.current_month = today.month
        self.current_year = today.year
        self.showing_next = False

        # Initialize the current month calendar using calendar service methods
        self.current_calendar = self.calendar.get_month_calendar(self.current_year, self.current_month)

        # Create header frame to position title and view buttons
        header_frame = tk.Frame(self.window)
        header_frame.grid(row=0, column=0, columnspan=7, sticky="ew", pady=5)
        header_frame.columnconfigure(1, weight=1)  # Make middle column expand

        # Week view button
        self.week_btn = tk.Button(header_frame, text="Week", command=self.open_week_view, font=("Arial", 10))
        self.week_btn.grid(row=0, column=2, sticky="e", padx=(5, 5))

        # Agenda view button
        self.agenda_btn = tk.Button(header_frame, text="Agenda", command=self.open_agenda_view, font=("Arial", 10))
        self.agenda_btn.grid(row=0, column=3, sticky="e", padx=(0, 10))

        self.header = tk.Label(header_frame, font=("Arial", 16, "bold"))
        self.header.grid(row=0, column=1)

        self.switch_btn = tk.Button(self.window, text="Show Next Month", command=self.switch_month)
        self.switch_btn.grid(row=1, column=0, columnspan=7, pady=5)

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
        success, message = self.calendar.save_all_calendars()
        print(message)
        self.window.destroy()

    def _get_month_calendar(self, year, month):
        """
        Get or create a MonthCalendar object for the specified year and month.
        Uses the calendar for data management.

        Args:
            year (int): The year for the calendar
            month (int): The month for the calendar

        Returns:
            MonthCalendar: The calendar object for the specified month
        """
        return self.calendar.get_month_calendar(year, month)

    def refresh_calendar_display(self):
        """
        Refresh the calendar display to show updated event highlighting.
        This method is called when events are added, modified, or deleted
        to ensure the calendar buttons reflect the current state of events.
        Updates the current calendar reference based on the displayed month.
        """
        if self.showing_next:
            year, month = self.calendar.calculate_next_month(self.current_year, self.current_month)
        else:
            year, month = self.current_year, self.current_month

        # Update the current calendar reference using service
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
            year, month = self.calendar.calculate_next_month(self.current_year, self.current_month)
            self.switch_btn.config(text="Show This Month")
        else:
            year, month = self.current_year, self.current_month
            self.switch_btn.config(text="Show Next Month")

        # Update the current calendar reference using service
        self.current_calendar = self._get_month_calendar(year, month)
        self.show_month(year, month)

    def open_week_view(self):
        """
        Open the week view for the current date.
        Creates a WeekViewGUI window showing the week containing today's date.
        """
        try:
            # Use today's date from service to open the week view
            today = self.calendar.get_today()
            # Get the calendar for today's month using service
            today_calendar = self._get_month_calendar(today.year, today.month)
            # Open week view
            WeekViewGUI_Class.WeekViewGUI(today_calendar, today.year, today.month, today.day, parent_gui=self)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred opening week view: {str(e)}")

    def open_agenda_view(self):
        """
        Open the agenda view showing all events across all months.
        Creates an AgendaViewGUI window displaying all events in chronological order.
        """
        try:
            # Use the current month calendar to access all events
            current_date = self.calendar.get_today()
            current_calendar = self._get_month_calendar(current_date.year, current_date.month)
            
            # Open agenda view
            AgendaViewGUI_Class.AgendaViewGUI(current_calendar, parent_gui=self)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred opening agenda view: {str(e)}")

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

            # Check if the date is current or future using service
            if clicked_date >= self.calendar.get_today():
                # Get the calendar for the clicked date's month using service
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
        
        # Use service for month display formatting
        self.header.config(text=self.calendar.format_month_display_name(year, month))

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
                    # Get today's date from service for highlighting
                    today = self.calendar.get_today()
                    if (year, month, day_num) == (today.year, today.month, today.day):
                        fg = "red"
                    else:
                        fg = "black"
                    
                    # Check for events using service
                    current_date = datetime.date(year, month, day_num)
                    has_events = self.calendar.has_events_on_date(month_calendar, current_date)
                    bg_color = "yellow" if has_events else None
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
                    # Add right-click context menu for week view option
                    day_button.bind("<Button-3>",
                                    lambda e, y=year, m=month, d=day_num: self.show_context_menu(e, y, m, d))
                    day_button.grid(row=row, column=col)
                    day_num += 1

                # Empty button for days after the month ends
                else:
                    tk.Button(self.frame, text="", width=15, height=7, state="disabled").grid(row=row, column=col)

            row += 1
            # Stop creating rows if we've placed all days and filled the current row
            if day_num > num_days and col == 6:
                break
