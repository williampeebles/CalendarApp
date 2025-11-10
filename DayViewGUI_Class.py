import tkinter as tk
import datetime
from tkcalendar import DateEntry


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
        # Create a new popup window (Toplevel creates a separate window)
        self.window = tk.Toplevel()

        # Set the window title using date formatting
        # strftime converts date to readable text like "Monday, November 02, 2025"
        self.window.title(f"Day View - {self.selected_date.strftime('%A, %B %d, %Y')}")

        # Set window size: 600 pixels wide, 500 pixels tall
        self.window.geometry("600x500")

        # Allow user to resize the window both horizontally and vertically
        self.window.resizable(True, True)

        # Create header section at top of window
        header_frame = tk.Frame(self.window)
        # pack() adds the frame to window, fill="x" makes it stretch horizontally
        # padx/pady add spacing around the frame
        header_frame.pack(fill="x", padx=10, pady=5)

        # Create a text label showing the date in large, bold font using service formatting
        header_label = tk.Label(
            header_frame,
            text=self.calendar.format_date_for_display(self.selected_date),
            font=("Arial", 18, "bold")  # Set font family, size, and style
        )
        # Add the label to the header frame
        header_label.pack()

        # Create a frame with border and title for the events section
        # LabelFrame creates a box with a title at the top
        events_frame = tk.LabelFrame(self.window, text="Events for this Day", font=("Arial", 12, "bold"))
        # fill="both" makes frame expand in all directions, expand=True allows it to grow
        events_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create container frame for the events list and scrollbar
        listbox_frame = tk.Frame(events_frame)
        listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create a vertical scrollbar for when there are many events
        scrollbar = tk.Scrollbar(listbox_frame)
        # Pack on right side, fill="y" makes it stretch vertically
        scrollbar.pack(side="right", fill="y")

        # Create the list box that will show all events for this day
        self.events_listbox = tk.Listbox(
            listbox_frame,
            yscrollcommand=scrollbar.set,  # Connect scrollbar to listbox
            font=("Arial", 10)
        )
        # Pack on left side, fill and expand to take up remaining space
        self.events_listbox.pack(side="left", fill="both", expand=True)

        # Connect scrollbar to listbox so they work together
        # When user moves scrollbar, it scrolls the listbox
        scrollbar.config(command=self.events_listbox.yview)

        # Create a horizontal container for all the buttons at bottom of window
        buttons_frame = tk.Frame(self.window)
        # fill="x" makes the frame stretch across the full width of window
        buttons_frame.pack(fill="x", padx=10, pady=5)

        # Create "Add New Event" button with green background
        add_btn = tk.Button(
            buttons_frame,
            text="Add New Event",  # Text shown on button
            command=self.add_event_dialog,  # Function to call when clicked
            font=("Arial", 10),  # Font style and size
            bg="lightgreen"  # Background color
        )
        # Pack on left side with some horizontal spacing
        add_btn.pack(side="left", padx=5)

        # Create "Edit Selected Event" button with blue background
        edit_btn = tk.Button(
            buttons_frame,
            text="Edit Selected Event",  # Button label
            command=self.edit_event_dialog,  # Function to call when clicked
            font=("Arial", 10),
            bg="lightblue"  # Light blue background
        )
        # Pack next to the Add button on the left side
        edit_btn.pack(side="left", padx=5)

        # Create "Delete Selected Event" button with red background
        delete_btn = tk.Button(
            buttons_frame,
            text="Delete Selected Event",  # Button label
            command=self.delete_event,  # Function to call when clicked
            font=("Arial", 10),
            bg="lightcoral"  # Light red/pink background for warning
        )
        # Pack next to other buttons on left side
        delete_btn.pack(side="left", padx=5)

        # Create "Close" button with default color
        close_btn = tk.Button(
            buttons_frame,
            text="Close",
            command=self.window.destroy,  # Destroy (close) the window when clicked
            font=("Arial", 10)
        )
        # Pack on right side (opposite end from other buttons)
        close_btn.pack(side="right", padx=5)

        # Initialize empty list to keep track of events for this day
        # This list is used later when user wants to edit or delete events
        self.current_events = []

        # Load and display all events for this day in the listbox
        self.refresh_events_list()

    def refresh_events_list(self):
        """Refresh the events listbox with current events for the selected date."""
        # Clear the listbox completely (remove all existing items)
        # delete(0, tk.END) removes from first item (0) to last item (END)
        self.events_listbox.delete(0, tk.END)

        # Convert the selected date to string format YYYY-MM-DD for database lookup
        # Example: converts datetime.date(2024, 11, 2) to "2024-11-02"
        date_str = self.selected_date.strftime("%Y-%m-%d")

        # Get all events that occur on this specific date from the calendar
        self.current_events = self.get_events_for_date(date_str)

        # Check if there are no events for this day
        if not self.current_events:
            # Add a message to listbox telling user there are no events
            self.events_listbox.insert(tk.END, "No events scheduled for this day")
        else:
            # Loop through each event and create a text description for display
            for event in self.current_events:
                # Build the display text based on event properties
                if event.is_all_day:
                    # For all-day events, show "All Day: Event Title"
                    event_text = f"All Day: {event.title}"
                else:
                    # For timed events, show "9:00 AM - 10:00 AM: Event Title"
                    event_text = f"{event.start_time} - {event.end_time}: {event.title}"

                # Add extra info if the event repeats
                if event.is_recurring:
                    event_text += f" (Repeats {event.recurrence_pattern})"

                # Add date range if event spans multiple days
                if event.start_day != event.end_day:
                    event_text += f" [{event.start_day} to {event.end_day}]"

                # Add this formatted text as a new item in the listbox
                # tk.END means add to the end of the list
                self.events_listbox.insert(tk.END, event_text)

    def get_events_for_date(self, date_str):
        """
        Get all events for a specific date from the calendar.

        Args:
            date_str (str): Date in YYYY-MM-DD format

        Returns:
            list: List of Event objects for the specified date
        """
        # Parse date string and get events using new calendar system
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return self.calendar.get_events_for_date(date_obj)
        except ValueError:
            print(f"Invalid date format: {date_str}")
            return []

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
        """
        Create and configure the dialog window.

        Args:
            title (str): Title of the dialog window

        Returns:
            tk.Toplevel: The configured dialog window
        """
        # Create a new popup window that sits on top of the main day view window
        dialog = tk.Toplevel(self.window)

        # Set the window title (like "Add New Event" or "Edit Event")
        dialog.title(title)

        # Set window size: 500 pixels wide, 600 pixels tall
        dialog.geometry("500x600")

        # Prevent user from resizing this dialog window
        dialog.resizable(False, False)

        # Make dialog modal (user must interact with this window before returning to main window)
        # transient() makes this window stay on top of parent window
        dialog.transient(self.window)
        # grab_set() captures all mouse/keyboard input until dialog is closed
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
                                     borderwidth=2, date_pattern='yyyy-mm-dd',  # Format: 2024-11-02
                                     mindate=datetime.date.today())  # Can't select past dates
        start_date_entry.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        # Set the default date to the currently selected day
        start_date_entry.set_date(self.selected_date)

        # Create label and date picker for event end date
        tk.Label(fields_frame, text="End Date:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        # Another DateEntry widget for the event end date (for multi-day events)
        end_date_entry = DateEntry(fields_frame, font=("Arial", 10), width=12,
                                   background='darkblue', foreground='white',
                                   borderwidth=2, date_pattern='yyyy-mm-dd',
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
            'recurring_var': recurring_var
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

        save_btn = tk.Button(
            button_frame,
            text="Save Event",
            command=lambda: self.save_event_data(
                form_fields['title_entry'], form_fields['start_date_entry'], form_fields['end_date_entry'],
                form_fields['start_time_entry'], form_fields['end_time_entry'], form_fields['description_text'],
                form_fields['recurring_var'], form_fields['all_day_var'], recurrence_var, event_index, dialog
            ),
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

    def save_event_data(self, title_entry, start_date_entry, end_date_entry, start_time_entry,
                        end_time_entry, description_text, recurring_var, all_day_var,
                        recurrence_var, event_index, dialog):
        """Save the event (add new or update existing) using calendar."""
        # Get form data
        title_text = title_entry.get().strip()
        start_date_obj = start_date_entry.get_date()
        end_date_obj = end_date_entry.get_date()
        start_time = start_time_entry.get().strip()
        end_time = end_time_entry.get().strip()
        description = description_text.get("1.0", tk.END).strip()
        is_recurring = recurring_var.get()
        is_all_day = all_day_var.get()
        recurrence_pattern = recurrence_var.get() if is_recurring else None

        if event_index is not None:
            # Update existing event using new calendar system
            selected_event = self.current_events[event_index]
            success, message = self.calendar.update_event(
                selected_event.event_id,
                title=title_text,
                date=start_date_obj,
                start_time=start_time,
                end_time=end_time,
                description=description,
                is_recurring=is_recurring,
                recurrence_pattern=recurrence_pattern,
                is_all_day=is_all_day
            )
        else:
            # Create new event using new calendar system
            success, message, event_id = self.calendar.create_event(
                title_text, start_date_obj, start_time, end_time,
                description, is_all_day, is_recurring, recurrence_pattern
            )

        # Handle result
        if success:
            # Refresh the events list and close dialog
            self.refresh_events_list()
            # Refresh the parent calendar display if available
            if self.parent_gui:
                self.parent_gui.refresh_calendar_display()
            dialog.destroy()
        else:
            # Show error message
            tk.messagebox.showerror("Error", message)

    def toggle_time_fields(self, all_day_var, start_time_entry, end_time_entry):
        """Enable or disable time fields based on all-day status."""
        # Check if the "All Day Event" checkbox is checked
        if all_day_var.get():
            # If all-day event, disable (gray out) the time input fields
            # config(state='disabled') makes the field uneditable and grayed out
            start_time_entry.config(state='disabled')
            end_time_entry.config(state='disabled')

            # Clear the time fields and show "All Day" instead
            # delete(0, tk.END) removes all text from beginning to end
            start_time_entry.delete(0, tk.END)
            start_time_entry.insert(0, "All Day")  # Insert "All Day" text at position 0
            end_time_entry.delete(0, tk.END)
            end_time_entry.insert(0, "All Day")
        else:
            # If not all-day event, enable the time input fields
            # config(state='normal') makes the field editable again
            start_time_entry.config(state='normal')
            end_time_entry.config(state='normal')

            # Clear fields and put back default times
            start_time_entry.delete(0, tk.END)
            start_time_entry.insert(0, "09:00 AM")  # Default start time
            end_time_entry.delete(0, tk.END)
            end_time_entry.insert(0, "10:00 AM")  # Default end time (1 hour later)

    def delete_event(self):
        """Delete the selected event after confirmation."""
        # Get which event is currently selected in the listbox
        selection = self.events_listbox.curselection()

        # Check if user actually selected something
        if not selection:
            tk.messagebox.showwarning("No Selection", "Please select an event to delete.")
            return

        # Get the index (position) of the selected item
        # selection[0] gets the first selected item (listbox allows multiple selections)
        selected_index = selection[0]

        # Make sure there are actual events and the selection is valid
        # Check if events list is empty or if selected index is beyond the list length
        if not self.current_events or selected_index >= len(self.current_events):
            tk.messagebox.showwarning("No Event", "No valid event selected to delete.")
            return

        # Get the actual event object that corresponds to the selected list item
        selected_event = self.current_events[selected_index]

        # Show confirmation dialog before deleting (prevent accidental deletions)
        # askyesno() returns True if user clicks "Yes", False if "No"
        confirm = tk.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the event '{selected_event.title}'?"
        )

        # Only proceed if user confirmed they want to delete
        if confirm:
            # Delete event using new calendar system
            success, message = self.calendar.delete_event(selected_event.event_id)

            # Check if the deletion was successful
            if success:
                # Refresh this day view to remove the deleted event from the list
                self.refresh_events_list()

                # If there's a parent month view window, refresh it too
                # This updates the month calendar to remove the event dot/indicator
                if self.parent_gui:
                    self.parent_gui.refresh_calendar_display()

                # Show success message to user
                tk.messagebox.showinfo("Success", message)
            else:
                # Show error message if deletion failed
                tk.messagebox.showerror("Error", message)