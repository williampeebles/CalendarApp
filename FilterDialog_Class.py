import tkinter as tk
import datetime
from tkcalendar import DateEntry
import calendar

class FilterDialog:
    """
    Dialog for filtering calendar events by various criteria.
    
    Allows users to filter events by:
    - Text search (title/description)
    - Date range
    - Event type (all-day, timed, recurring)
    """
    
    def __init__(self, parent, calendar_service):
        """
        Initialize the filter dialog.
        
        Args:
            parent: Parent window
            calendar_service: CalendarService instance
        """
        self.calendar = calendar_service
        self.result = None  # Will store filter criteria
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Filter Events")
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all filter option widgets."""
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Search text filter
        tk.Label(main_frame, text="Search Text:", font=("Arial", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5
        )
        self.search_entry = tk.Entry(main_frame, font=("Arial", 10), width=30)
        self.search_entry.grid(row=0, column=1, pady=5, padx=5)
        tk.Label(main_frame, text="(searches title and description)", 
                font=("Arial", 8, "italic"), fg="gray").grid(
            row=1, column=1, sticky="w", padx=5
        )
        
        # Date range filters
        tk.Label(main_frame, text="Date Range:", font=("Arial", 10, "bold")).grid(
            row=2, column=0, sticky="w", pady=(15, 5)
        )
        
        # From date
        tk.Label(main_frame, text="From:", font=("Arial", 10)).grid(
            row=3, column=0, sticky="e", pady=5, padx=5
        )
        
        self.from_date = DateEntry(
            main_frame, font=("Arial", 10), width=12,
            background='darkblue', foreground='white',
            borderwidth=2, date_pattern='dd-mm-yyyy'
        )
        self.from_date.grid(row=3, column=1, sticky="w", pady=5, padx=5)
        
        # To date
        tk.Label(main_frame, text="To:", font=("Arial", 10)).grid(
            row=4, column=0, sticky="e", pady=5, padx=5
        )
        self.to_date = DateEntry(
            main_frame, font=("Arial", 10), width=12,
            background='darkblue', foreground='white',
            borderwidth=2, date_pattern='dd-mm-yyyy'
        )
        self.to_date.grid(row=4, column=1, sticky="w", pady=5, padx=5)
        
        # Set default date range (current month)
        today = datetime.date.today()
        self.from_date.set_date(today)
        # Set to_date to end of current month
        import calendar
        last_day = calendar.monthrange(today.year, today.month)[1]
        self.to_date.set_date(datetime.date(today.year, today.month, last_day))
        
        # Event type filters
        tk.Label(main_frame, text="Event Type:", font=("Arial", 10, "bold")).grid(
            row=5, column=0, sticky="w", pady=(15, 5)
        )
        
        self.show_all_day = tk.BooleanVar(value=True)
        self.show_timed = tk.BooleanVar(value=True)
        self.show_recurring = tk.BooleanVar(value=True)
        
        tk.Checkbutton(main_frame, text="All-Day Events", variable=self.show_all_day,
                      font=("Arial", 9)).grid(row=6, column=1, sticky="w", padx=5)
        tk.Checkbutton(main_frame, text="Timed Events", variable=self.show_timed,
                      font=("Arial", 9)).grid(row=7, column=1, sticky="w", padx=5)
        tk.Checkbutton(main_frame, text="Recurring Events", variable=self.show_recurring,
                      font=("Arial", 9)).grid(row=8, column=1, sticky="w", padx=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(button_frame, text="Apply Filter", command=self.apply_filter,
                 font=("Arial", 10), bg="lightgreen").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Clear All", command=self.clear_filters,
                 font=("Arial", 10), bg="lightyellow").pack(side="left", padx=5)
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 font=("Arial", 10)).pack(side="right", padx=5)
    
    def apply_filter(self):
        """Collect filter criteria and close dialog."""
        self.result = {
            'search_text': self.search_entry.get().strip().lower(),
            'from_date': self.from_date.get_date(),
            'to_date': self.to_date.get_date(),
            'show_all_day': self.show_all_day.get(),
            'show_timed': self.show_timed.get(),
            'show_recurring': self.show_recurring.get()
        }
        self.dialog.destroy()
    
    def clear_filters(self):
        """Reset all filter options to defaults."""
        self.search_entry.delete(0, tk.END)
        today = datetime.date.today()
        self.from_date.set_date(today)
        last_day = calendar.monthrange(today.year, today.month)[1]
        self.to_date.set_date(datetime.date(today.year, today.month, last_day))
        self.show_all_day.set(True)
        self.show_timed.set(True)
        self.show_recurring.set(True)