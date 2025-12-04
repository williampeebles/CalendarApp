import tkinter as tk
from CalendarService import CalendarService
from MonthViewService_Class import MonthViewService
import DayViewGUI_Class
import WeekViewGUI_Class
import AgendaViewGUI_Class
import datetime
import calendar
from tkinter import messagebox


class MonthViewGUI:
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
        month_calendars (dict): Dictionary storing Calendar objects by month key
        current_calendar (Calendar): Currently active month calendar
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
        self.calendar = calendar_obj if calendar_obj else CalendarService()
        self.month_service = MonthViewService(self.calendar)
        self.window = tk.Tk()
        self.window.title("Month View Calendar")

        # Get current date from calendar
        today = self.calendar.get_today()
        self.current_month = today.month
        self.current_year = today.year
        self.showing_next = False

        # Store current month and year for display
        # No need for current_calendar with new architecture

        # Create button frame for view buttons (top row)
        button_frame = tk.Frame(self.window)
        button_frame.grid(row=0, column=0, columnspan=7, sticky="ew", pady=(5, 2))

        # Create inner frame to center the buttons
        button_container = tk.Frame(button_frame)
        button_container.pack(expand=True)

        # Week view button
        self.week_btn = tk.Button(button_container, text="Week", command=self.open_week_view, font=("Arial", 10))
        self.week_btn.pack(side="left", padx=(0, 5))

        # Agenda view button
        self.agenda_btn = tk.Button(button_container, text="Agenda", command=self.open_agenda_view, font=("Arial", 10))
        self.agenda_btn.pack(side="left", padx=(5, 5))

        # Filter button
        self.filter_btn = tk.Button(button_container, text="Filter", command=self.open_filter, font=("Arial", 10))
        self.filter_btn.pack(side="left", padx=(5, 0))

        # Create header frame for month/year title (centered)
        header_frame = tk.Frame(self.window)
        header_frame.grid(row=1, column=0, columnspan=7, sticky="ew", pady=(2, 5))

        self.header = tk.Label(header_frame, font=("Arial", 16, "bold"), anchor="center")
        self.header.pack(fill="x")

        self.switch_btn = tk.Button(self.window, text="Show Next Month", command=self.switch_month)
        self.switch_btn.grid(row=2, column=0, columnspan=7, pady=5)

        self.frame = tk.Frame(self.window)
        self.frame.grid(row=3, column=0, columnspan=7)

        # Set up window close protocol to save data
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.show_month(self.current_year, self.current_month)
        self.window.mainloop()

    def on_closing(self):
        """
        Handle window closing event.
        """
        print("Closing calendar application...")
        self.window.destroy()

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
            year, month = self.month_service.calculate_next_month(self.current_year, self.current_month)
            self.switch_btn.config(text="Show This Month")
        else:
            year, month = self.current_year, self.current_month
            self.switch_btn.config(text="Show Next Month")

        # With new architecture, just show the month
        self.show_month(year, month)

    def open_week_view(self):
        """
        Open the week view for the current date.
        Creates a WeekViewGUI window showing the week containing today's date.
        """
        try:
            # Use today's date from service to open the week view
            today = self.calendar.get_today()
            # Open week view with the main calendar
            WeekViewGUI_Class.WeekViewGUI(self.calendar, today.year, today.month, today.day, parent_gui=self)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred opening week view: {str(e)}")

    def open_agenda_view(self):
        """
        Open the agenda view showing all events across all months.
        Creates an AgendaViewGUI window displaying all events in chronological order.
        """
        try:
            # Open agenda view with the main calendar
            AgendaViewGUI_Class.AgendaViewGUI(self.calendar, parent_gui=self)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred opening agenda view: {str(e)}")

    def open_filter(self):
        """
        Open filter dialog and display filtered events in agenda view.
        """
        try:
            from FilterDialog_Class import FilterDialog
            
            # Open filter dialog
            filter_dialog = FilterDialog(self.window, self.calendar)
            self.window.wait_window(filter_dialog.dialog)
            
            # If user applied filters, open agenda view with filtered results
            if filter_dialog.result:
                # Get all events
                all_events = self.month_service.get_events_for_all_months()
                
                # Apply filters
                filtered_events = self.calendar.filter_events(all_events, filter_dialog.result)
                
                # Open agenda view with filtered events
                AgendaViewGUI_Class.FilteredAgendaViewGUI(
                    self.calendar, 
                    filtered_events, 
                    filter_dialog.result,
                    parent_gui=self
                )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred with filtering: {str(e)}")

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
                # Open day view for valid dates with the main calendar
                DayViewGUI_Class.DayViewGUI(self.calendar, year, month, day, parent_gui=self)
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
        # With new architecture, we use the main calendar for all months

        for widget in self.frame.winfo_children():
            widget.destroy()

        # Use service for month display formatting
        self.header.config(text=self.month_service.format_month_display_name(year, month))

        days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        col = 0
        while col < 7:
            tk.Label(self.frame, text=days_of_the_week[col], width=15, height=2,
                     font=("Arial", 10, "bold"), relief="ridge", bd=1).grid(row=0, column=col, sticky="nsew")
            self.frame.columnconfigure(col, weight=1, minsize=105)
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
                    # Empty frame for days before the month starts
                    empty_frame = tk.Frame(self.frame, bg="SystemButtonFace", height=105, relief="raised", bd=2)
                    empty_frame.grid(row=row, column=col, sticky="nsew")

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
                    has_events = self.month_service.has_events_on_date(current_date)
                    bg_color = "yellow" if has_events else None
                    
                    # Create a frame to hold button content
                    day_frame = tk.Frame(self.frame, bg=bg_color if bg_color else "SystemButtonFace", 
                                        height=105, relief="raised", bd=2)
                    day_frame.grid(row=row, column=col, sticky="nsew")
                    
                    # Make the frame clickable
                    day_frame.bind("<Button-1>", lambda e, y=year, m=month, d=day_num: self.on_day_click(y, m, d))
                    
                    # Add day number in top right corner
                    day_label = tk.Label(day_frame, text=str(day_num), fg=fg, bg=bg_color if bg_color else "SystemButtonFace",
                                        font=("Arial", 10))
                    day_label.place(relx=0.95, rely=0.05, anchor="ne")
                    day_label.bind("<Button-1>", lambda e, y=year, m=month, d=day_num: self.on_day_click(y, m, d))
                    
                    # Add event count in center if there are events
                    if has_events:
                        events_on_date = self.month_service.get_events_for_date(current_date)
                        event_count = len(events_on_date)
                        event_text = f"({event_count} event{'s' if event_count != 1 else ''})"
                        event_label = tk.Label(day_frame, text=event_text, bg=bg_color, fg="black",
                                              font=("Arial", 9))
                        event_label.place(relx=0.5, rely=0.5, anchor="center")
                        event_label.bind("<Button-1>", lambda e, y=year, m=month, d=day_num: self.on_day_click(y, m, d))
                    
                    # Add right-click context menu for week view option
                    day_frame.bind("<Button-3>",
                                    lambda e, y=year, m=month, d=day_num: self.show_context_menu(e, y, m, d))
                    day_num += 1

                # Empty frame for days after the month ends
                else:
                    empty_frame = tk.Frame(self.frame, bg="SystemButtonFace", height=105, relief="raised", bd=2)
                    empty_frame.grid(row=row, column=col, sticky="nsew")

            row += 1
            # Stop creating rows if we've placed all days and filled the current row
            if day_num > num_days and col == 6:
                break
