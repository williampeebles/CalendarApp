import tkinter as tk
import datetime
import tkinter.messagebox as messagebox
from tkcalendar import DateEntry

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
                if event.is_all_day:
                    event_text = f"All Day: {event.title}"
                else:
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

        # All day checkbox
        all_day_var = tk.BooleanVar()

        def toggle_time_fields():
            """Enable or disable time fields based on all-day status."""
            if all_day_var.get():
                start_time_entry.config(state='disabled')
                end_time_entry.config(state='disabled')
                start_time_entry.delete(0, tk.END)
                start_time_entry.insert(0, "All Day")
                end_time_entry.delete(0, tk.END)
                end_time_entry.insert(0, "All Day")
            else:
                start_time_entry.config(state='normal')
                end_time_entry.config(state='normal')
                start_time_entry.delete(0, tk.END)
                start_time_entry.insert(0, "09:00 AM")
                end_time_entry.delete(0, tk.END)
                end_time_entry.insert(0, "10:00 AM")

        all_day_check = tk.Checkbutton(
            fields_frame,
            text="All Day Event",
            variable=all_day_var,
            font=("Arial", 10),
            command=toggle_time_fields
        )
        all_day_check.grid(row=5, column=1, sticky="w", pady=5)

        # Description field
        tk.Label(fields_frame, text="Description:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="nw",
                                                                                     pady=5)
        description_text = tk.Text(fields_frame, font=("Arial", 10), width=30, height=4)
        description_text.grid(row=6, column=1, columnspan=2, pady=5, padx=5, sticky="w")

        # Recurring checkbox
        recurring_var = tk.BooleanVar()
        recurring_check = tk.Checkbutton(
            fields_frame,
            text="Recurring Event",
            variable=recurring_var,
            font=("Arial", 10),
            command=lambda: self.toggle_recurrence_options(recurring_var.get(), recurrence_frame)
        )
        recurring_check.grid(row=7, column=1, sticky="w", pady=5)

        # Recurrence options frame (initially hidden)
        recurrence_frame = tk.LabelFrame(fields_frame, text="Recurrence Options", font=("Arial", 9, "bold"))
        recurrence_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
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

            # Set all-day status first
            all_day_var.set(existing_event.is_all_day)

            if existing_event.is_all_day:
                # For all-day events, disable time fields and show "All Day"
                start_time_entry.config(state='disabled')
                end_time_entry.config(state='disabled')
                start_time_entry.delete(0, tk.END)
                start_time_entry.insert(0, "All Day")
                end_time_entry.delete(0, tk.END)
                end_time_entry.insert(0, "All Day")
            else:
                # For timed events, set the actual times
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
            is_all_day = all_day_var.get()
            recurrence_pattern = recurrence_var.get() if is_recurring else None

            # Validation
            if not title_text:
                tk.messagebox.showerror("Error", "Event title is required.")
                return

            # For all-day events, set standard times or skip time validation
            if is_all_day:
                start_time = "All Day"
                end_time = "All Day"
            else:
                if not start_time or not end_time:
                    tk.messagebox.showerror("Error", "Start and end times are required for timed events.")
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

            if title_text and start_date and end_date:
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
                        new_end_day=end_date,  # Assuming end_day is the same as end_date
                        new_all_day=is_all_day
                    )
                else:
                    # New event, generate unique ID using the calendar's method
                    try:
                        event_id = self.calendar.calendar.generate_event_id()
                    except Exception as e:
                        tk.messagebox.showerror("Error", str(e))
                        return

                    # Add event to calendar - this will automatically save to database if using MonthCalendar
                    self.calendar.add_event(
                        event_id, title_text, self.selected_date.strftime("%Y-%m-%d"),
                        start_date, end_date, start_time, end_time, description,
                        is_recurring, recurrence_pattern, is_all_day
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
