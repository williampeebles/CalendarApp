import tkinter as tk

import datetime
from tkcalendar import DateEntry
from DayViewService_Class import DayViewService


class DayViewGUI:
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

    # UI Constants
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 500
    DIALOG_WIDTH = 500
    DIALOG_HEIGHT = 600
    HEADER_FONT = ("Arial", 18, "bold")
    SECTION_FONT = ("Arial", 12, "bold")
    LABEL_FONT = ("Arial", 10, "bold")
    NORMAL_FONT = ("Arial", 10)
    SMALL_FONT = ("Arial", 9)
    BUTTON_PADDING = 5
    FRAME_PADDING = 10
    DEFAULT_START_TIME = "09:00 AM"
    DEFAULT_END_TIME = "10:00 AM"

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
        # Store the calendar object for all event operations
        self.calendar = calendar_obj
        self.day_service = DayViewService(self.calendar)

        # Create a date object from the year, month, day numbers passed in
        # This converts separate numbers (2024, 11, 15) into a single date object
        self.selected_date = datetime.date(year, month, day)

        # Keep reference to parent window so we can refresh it when events change
        self.parent_gui = parent_gui

        # Check if the date is valid (current or future) using calendar
        if self.selected_date < self.calendar.get_today():
            # Show a warning popup if user tries to view past dates
            tk.messagebox.showwarning("Invalid Date", "Cannot view or edit events for past dates.")
            # Exit early - don't create the window if date is invalid
            return

        # If date is valid, create and show the day view window
        self.create_day_view_window()

    def create_day_view_window(self):
        """Create and setup the day view window with all components."""
        self.window = tk.Toplevel()
        self.window.title(f"Day View - {self.selected_date.strftime('%d-%m-%Y')}")
        self.window.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.window.resizable(True, True)

        header_frame = tk.Frame(self.window)
        header_frame.pack(fill="x", padx=self.FRAME_PADDING, pady=5)

        header_label = tk.Label(
            header_frame,
            text=self.day_service.format_date_for_display(self.selected_date),
            font=self.HEADER_FONT
        )
        header_label.pack()

        events_frame = tk.LabelFrame(self.window, text="Events for this Day", font=self.SECTION_FONT)
        events_frame.pack(fill="both", expand=True, padx=self.FRAME_PADDING, pady=5)

        listbox_frame = tk.Frame(events_frame)
        listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side="right", fill="y")

        self.events_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=self.NORMAL_FONT)
        self.events_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.events_listbox.yview)

        buttons_frame = tk.Frame(self.window)
        buttons_frame.pack(fill="x", padx=self.FRAME_PADDING, pady=5)

        tk.Button(buttons_frame, text="Add New Event", command=self.add_event_dialog,
                  font=self.NORMAL_FONT, bg="lightgreen").pack(side="left", padx=self.BUTTON_PADDING)
        
        tk.Button(buttons_frame, text="Edit Selected Event", command=self.edit_event_dialog,
                  font=self.NORMAL_FONT, bg="lightblue").pack(side="left", padx=self.BUTTON_PADDING)
        
        tk.Button(buttons_frame, text="Delete Selected Event", command=self.delete_event,
                  font=self.NORMAL_FONT, bg="lightcoral").pack(side="left", padx=self.BUTTON_PADDING)
        
        tk.Button(buttons_frame, text="Close", command=self.window.destroy,
                  font=self.NORMAL_FONT).pack(side="right", padx=self.BUTTON_PADDING)

        self.current_events = []
        self.refresh_events_list()

    def refresh_events_list(self):
        """Refresh the events listbox with current events for the selected date."""
        self.events_listbox.delete(0, tk.END)
        self.current_events = self.day_service.get_events_for_date(self.selected_date)

        if not self.current_events:
            self.events_listbox.insert(tk.END, "No events scheduled for this day")
        else:
            for event in self.current_events:
                event_text = self._format_event_for_display(event)
                self.events_listbox.insert(tk.END, event_text)

    def _format_event_for_display(self, event):
        """Format an event for display in the listbox."""
        if event.is_all_day:
            event_text = f"All Day: {event.title}"
        else:
            event_text = f"{event.start_time} - {event.end_time}: {event.title}"

        if event.is_recurring:
            event_text += f" (Repeats {event.recurrence_pattern})"

        if event.start_day != event.end_day:
            event_text += f" [{event.start_day} to {event.end_day}]"

        return event_text

    def toggle_recurrence_options(self, show, recurrence_frame):
        """Show or hide the recurrence options frame."""
        if show:
            # Make the recurrence options visible by adding them back to the layout
            recurrence_frame.grid()
        else:
            # Hide the recurrence options by removing them from the layout
            # grid_remove() hides the widget but remembers its position
            recurrence_frame.grid_remove()

    def add_event_dialog(self):
        """Open a dialog to create a new event for the selected date."""
        # Call the main form dialog with "Add" title and no event index (new event)
        self.event_form_dialog("Add New Event")

    def edit_event_dialog(self):
        """Open a dialog to edit the selected event."""
        # Get which item is currently selected in the events listbox
        # curselection() returns a tuple of selected indices
        selection = self.events_listbox.curselection()

        # Check if user actually selected an event
        if not selection:
            # Show warning if no event is selected
            tk.messagebox.showwarning("No Selection", "Please select an event to edit.")
            return

        # Call the form dialog with "Edit" title and the index of selected event
        # selection[0] gets the first (and only) selected item's index
        self.event_form_dialog("Edit Event", selection[0])

    def event_form_dialog(self, title, event_index=None):
        """
        Create a form dialog for adding or editing events.

        Args:
            title (str): Title of the dialog window
            event_index (int, optional): Index of event to edit (None for new event)
        """
        # Step 1: Create the popup dialog window with title
        dialog = self.create_form_dialog_window(title)

        # Step 2: Create all the input fields (title, date, time, etc.) and get references to them
        fields_frame, form_fields = self.create_form_fields(dialog)

        # Step 3: Create the recurring event options section
        recurrence_frame, recurrence_var = self.create_recurrence_options(fields_frame, form_fields['recurring_var'])

        # Step 4: If editing existing event, fill in the form with current values
        if event_index is not None and self.current_events:
            self.populate_form_for_editing(event_index, form_fields, recurrence_var, recurrence_frame)

        # Step 5: Create Save and Cancel buttons at bottom of form
        self.create_form_buttons(dialog, form_fields, recurrence_var, event_index)

    def create_form_dialog_window(self, title):
        """Create and configure the dialog window."""
        dialog = tk.Toplevel(self.window)
        dialog.title(title)
        dialog.geometry(f"{self.DIALOG_WIDTH}x{self.DIALOG_HEIGHT}")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        return dialog

    def create_form_fields(self, dialog):
        """
        Create all form input fields.

        Args:
            dialog (tk.Toplevel): The dialog window

        Returns:
            tuple: (fields_frame, form_fields_dict)
        """
        # Create a container frame to hold all the form input fields
        fields_frame = tk.Frame(dialog)
        # Pack with padding and allow it to expand to fill available space
        fields_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create label and input field for event title
        # Label shows "Event Title:" in bold font
        tk.Label(fields_frame, text="Event Title:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w",
                                                                                     pady=5)
        # Entry widget for user to type the event name
        title_entry = tk.Entry(fields_frame, font=("Arial", 10), width=30)
        # Place in grid: row 0, column 1, span across 2 columns, align to left (west)
        title_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5, sticky="w")

        # Create label and date picker for event start date
        tk.Label(fields_frame, text="Start Date:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        # DateEntry is a special widget that shows a calendar popup for date selection
        start_date_entry = DateEntry(fields_frame, font=("Arial", 10), width=12,
                                     background='darkblue', foreground='white',  # Color scheme
                                     borderwidth=2, date_pattern='dd-mm-yyyy',  # Format: 16-11-2025
                                     mindate=datetime.date.today())  # Can't select past dates
        start_date_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        # Set the default date to the currently selected day
        start_date_entry.set_date(self.selected_date)

        # Create label and date picker for event end date
        tk.Label(fields_frame, text="End Date:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        # Another DateEntry widget for the event end date (for multi-day events)
        end_date_entry = DateEntry(fields_frame, font=("Arial", 10), width=12,
                                   background='darkblue', foreground='white',
                                   borderwidth=2, date_pattern='dd-mm-yyyy',
                                   mindate=datetime.date.today())
        end_date_entry.grid(row=2, column=1, pady=5, padx=5, sticky="w")
        # Default end date is same as start date (single day event)
        end_date_entry.set_date(self.selected_date)

        # Create label and input field for event start time
        tk.Label(fields_frame, text="Start Time:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        # Regular text entry for start time (user types "9:00 AM" format)
        start_time_entry = tk.Entry(fields_frame, font=("Arial", 10), width=15)
        start_time_entry.grid(row=3, column=1, pady=5, padx=5, sticky="w")
        # Pre-fill with default start time of 9:00 AM
        start_time_entry.insert(0, "09:00 AM")

        # Create label and input field for event end time
        tk.Label(fields_frame, text="End Time:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=5)
        # Regular text entry for end time
        end_time_entry = tk.Entry(fields_frame, font=("Arial", 10), width=15)
        end_time_entry.grid(row=4, column=1, pady=5, padx=5, sticky="w")
        # Pre-fill with default end time of 10:00 AM (1 hour event)
        end_time_entry.insert(0, "10:00 AM")

        # Create checkbox for "All Day Event" option
        # BooleanVar() stores True/False value for checkbox state
        all_day_var = tk.BooleanVar()
        all_day_check = tk.Checkbutton(
            fields_frame,
            text="All Day Event",  # Text shown next to checkbox
            variable=all_day_var,  # Variable that stores checked state
            font=("Arial", 10),
            # When clicked, call toggle_time_fields to enable/disable time inputs
            command=lambda: self.toggle_time_fields(all_day_var, start_time_entry, end_time_entry)
        )
        all_day_check.grid(row=5, column=1, sticky="w", pady=5)

        # Create label and text area for event description
        # sticky="nw" means align to top-left (north-west) since text area is tall
        tk.Label(fields_frame, text="Description:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="nw",
                                                                                     pady=5)
        # Text widget allows multiple lines of text input (unlike Entry which is single line)
        description_text = tk.Text(fields_frame, font=("Arial", 10), width=30, height=4)
        description_text.grid(row=6, column=1, columnspan=2, pady=5, padx=5, sticky="w")
        
        # Character counter for description (80 character limit)
        char_count_label = tk.Label(fields_frame, text="0/80 characters", font=("Arial", 8), fg="gray")
        char_count_label.grid(row=7, column=1, sticky="w", padx=5)
        
        # Update character count as user types
        def update_char_count(event=None):
            text = description_text.get("1.0", tk.END).strip()
            count = len(text)
            char_count_label.config(text=f"{count}/80 characters")
            # Change color if over limit
            if count > 80:
                char_count_label.config(fg="red")
            else:
                char_count_label.config(fg="gray")
        
        description_text.bind("<KeyRelease>", update_char_count)

        # Create variable to store whether this is a recurring event
        recurring_var = tk.BooleanVar()

        # Store all form fields in a dictionary for easy access
        form_fields = {
            'title_entry': title_entry,
            'start_date_entry': start_date_entry,
            'end_date_entry': end_date_entry,
            'start_time_entry': start_time_entry,
            'end_time_entry': end_time_entry,
            'all_day_var': all_day_var,
            'description_text': description_text,
            'recurring_var': recurring_var,
            'char_count_label': char_count_label,
            'update_char_count': update_char_count
        }

        return fields_frame, form_fields

    def create_recurrence_options(self, fields_frame, recurring_var):
        """
        Create the recurrence options section.

        Args:
            fields_frame (tk.Frame): The main fields frame
            recurring_var (tk.BooleanVar): The recurring checkbox variable

        Returns:
            tuple: (recurrence_frame, recurrence_var)
        """
        # Recurring checkbox
        recurring_check = tk.Checkbutton(
            fields_frame,
            text="Recurring Event",
            variable=recurring_var,
            font=("Arial", 10),
            command=lambda: self.toggle_recurrence_options(recurring_var.get(), recurrence_frame)
        )
        recurring_check.grid(row=8, column=1, sticky="w", pady=5)

        # Recurrence options frame (initially hidden)
        recurrence_frame = tk.LabelFrame(fields_frame, text="Recurrence Options", font=("Arial", 9, "bold"))
        recurrence_frame.grid(row=9, column=0, columnspan=3, sticky="ew", pady=10, padx=5)
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

        return recurrence_frame, recurrence_var

    def populate_form_for_editing(self, event_index, form_fields, recurrence_var, recurrence_frame):
        """
        Populate form fields with existing event data for editing.

        Args:
            event_index (int): Index of the event to edit
            form_fields (dict): Dictionary containing all form field widgets
            recurrence_var (tk.StringVar): Recurrence pattern variable
            recurrence_frame (tk.LabelFrame): Recurrence options frame
        """
        existing_event = self.current_events[event_index]

        # Populate basic fields
        form_fields['title_entry'].insert(0, existing_event.title)

        # Parse and set start/end dates
        try:
            start_date_obj = datetime.datetime.strptime(existing_event.start_day, "%Y-%m-%d").date()
            end_date_obj = datetime.datetime.strptime(existing_event.end_day, "%Y-%m-%d").date()
            form_fields['start_date_entry'].set_date(start_date_obj)
            form_fields['end_date_entry'].set_date(end_date_obj)
        except ValueError:
            # Fallback to selected date if parsing fails
            pass

        # Set all-day status first
        form_fields['all_day_var'].set(existing_event.is_all_day)

        if existing_event.is_all_day:
            # For all-day events, disable time fields and show "All Day"
            form_fields['start_time_entry'].config(state='disabled')
            form_fields['end_time_entry'].config(state='disabled')
            form_fields['start_time_entry'].delete(0, tk.END)
            form_fields['start_time_entry'].insert(0, "All Day")
            form_fields['end_time_entry'].delete(0, tk.END)
            form_fields['end_time_entry'].insert(0, "All Day")
        else:
            # For timed events, set the actual times
            form_fields['start_time_entry'].delete(0, tk.END)
            form_fields['start_time_entry'].insert(0, existing_event.start_time)
            form_fields['end_time_entry'].delete(0, tk.END)
            form_fields['end_time_entry'].insert(0, existing_event.end_time)

        form_fields['description_text'].insert("1.0", existing_event.description)
        
        # Update character counter after inserting description
        if 'update_char_count' in form_fields:
            form_fields['update_char_count']()

        # Set recurrence options
        form_fields['recurring_var'].set(existing_event.is_recurring)
        if existing_event.is_recurring and existing_event.recurrence_pattern:
            recurrence_var.set(existing_event.recurrence_pattern)
            self.toggle_recurrence_options(True, recurrence_frame)

    def create_form_buttons(self, dialog, form_fields, recurrence_var, event_index):
        """
        Create the save and cancel buttons for the form.

        Args:
            dialog (tk.Toplevel): The dialog window
            form_fields (dict): Dictionary containing all form field widgets
            recurrence_var (tk.StringVar): Recurrence pattern variable
            event_index (int, optional): Index of event to edit (None for new event)
        """
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            button_frame, text="Save Event",
            command=lambda: self.save_event_data(form_fields, recurrence_var, event_index, dialog),
            font=self.NORMAL_FONT, bg="lightgreen"
        ).pack(side="left", padx=self.BUTTON_PADDING)

        tk.Button(
            button_frame, text="Cancel",
            command=dialog.destroy,
            font=self.NORMAL_FONT
        ).pack(side="right", padx=self.BUTTON_PADDING)

    def _extract_form_data(self, form_fields, recurrence_var):
        """Extract data from form widgets into a dictionary."""
        return {
            'title': form_fields['title_entry'].get().strip(),
            'start_date': form_fields['start_date_entry'].get_date(),
            'end_date': form_fields['end_date_entry'].get_date(),
            'start_time': form_fields['start_time_entry'].get().strip(),
            'end_time': form_fields['end_time_entry'].get().strip(),
            'description': form_fields['description_text'].get("1.0", tk.END).strip(),
            'is_all_day': form_fields['all_day_var'].get(),
            'is_recurring': form_fields['recurring_var'].get(),
            'recurrence_pattern': recurrence_var.get() if form_fields['recurring_var'].get() else None
        }

    def save_event_data(self, form_fields, recurrence_var, event_index, dialog):
        """Save the event (add new or update existing) using calendar."""
        form_data = self._extract_form_data(form_fields, recurrence_var)

        if event_index is not None:
            selected_event = self.current_events[event_index]
            success, message = self.day_service.update_event(
                selected_event.event_id,
                title=form_data['title'],
                date=form_data['start_date'],
                start_time=form_data['start_time'],
                end_time=form_data['end_time'],
                description=form_data['description'],
                is_recurring=form_data['is_recurring'],
                recurrence_pattern=form_data['recurrence_pattern'],
                is_all_day=form_data['is_all_day']
            )
        else:
            success, message, event_id = self.day_service.create_event(
                form_data['title'], form_data['start_date'], form_data['start_time'], form_data['end_time'],
                form_data['description'], form_data['is_all_day'], form_data['is_recurring'], form_data['recurrence_pattern']
            )

        if success:
            self.refresh_events_list()
            if self.parent_gui:
                self.parent_gui.refresh_calendar_display()
            dialog.destroy()
        else:
            tk.messagebox.showerror("Error", message)

    def toggle_time_fields(self, all_day_var, start_time_entry, end_time_entry):
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
            start_time_entry.insert(0, self.DEFAULT_START_TIME)
            end_time_entry.delete(0, tk.END)
            end_time_entry.insert(0, self.DEFAULT_END_TIME)

    def delete_event(self):
        """Delete the selected event after confirmation."""
        selection = self.events_listbox.curselection()

        if not selection:
            tk.messagebox.showwarning("No Selection", "Please select an event to delete.")
            return

        selected_index = selection[0]

        if not self.current_events or selected_index >= len(self.current_events):
            tk.messagebox.showwarning("No Event", "No valid event selected to delete.")
            return

        selected_event = self.current_events[selected_index]

        # Check if it's a recurring event
        delete_all = False
        if selected_event.is_recurring:
            # Ask user if they want to delete all instances
            response = tk.messagebox.askyesnocancel(
                "Delete Recurring Event",
                f"'{selected_event.title}' is a recurring event.\n\n"
                f"Yes = Delete ALL occurrences ({selected_event.recurrence_pattern})\n"
                f"No = Delete only THIS occurrence\n"
                f"Cancel = Don't delete"
            )
            
            if response is None:  # Cancel
                return
            delete_all = response  # True = delete all, False = delete single
        else:
            # Regular event confirmation
            confirm = tk.messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete the event '{selected_event.title}'?"
            )
            if not confirm:
                return

        success, message = self.day_service.delete_event(selected_event.event_id, delete_all_recurring=delete_all)

        if success:
            self.refresh_events_list()
            if self.parent_gui:
                self.parent_gui.refresh_calendar_display()
            tk.messagebox.showinfo("Success", message)
        else:
            tk.messagebox.showerror("Error", message)
