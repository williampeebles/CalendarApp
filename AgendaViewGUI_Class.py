import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import datetime

class AgendaViewGUI():
    """
    A GUI class that displays all events in a scrollable agenda/list format.

    This class creates a window interface that shows all events from the calendar
    in chronological order, providing an overview of all scheduled events.
    Users can view, edit, and delete events from this comprehensive list.

    Attributes:
        calendar (Calendar): Reference to the main calendar object
        window (tk.Toplevel): The agenda view window
        events_tree (ttk.Treeview): Tree widget displaying all events
        parent_gui (MonthViewGUI, optional): Reference to parent for refreshing
    """

    def __init__(self, calendar_obj, parent_gui=None):
        """
        Initialize the AgendaViewGUI.

        Args:
            calendar_obj (Calendar): The calendar object containing events
            parent_gui (MonthViewGUI, optional): Reference to parent month view for refreshing
        """
        # Store reference to calendar object so we can access all events
        self.calendar = calendar_obj
        
        # Keep reference to parent window so we can refresh it when events change
        self.parent_gui = parent_gui
        
        # Create and show the agenda view window
        self.create_agenda_window()

    def create_agenda_window(self):
        """Create and setup the agenda view window with all components."""
        # Create a new popup window (Toplevel creates a separate window)
        self.window = tk.Toplevel()
        
        # Set the window title
        self.window.title("Agenda View - All Events")
        
        # Set window size: 800 pixels wide, 600 pixels tall (larger for list view)
        self.window.geometry("800x600")
        
        # Allow user to resize the window both horizontally and vertically
        self.window.resizable(True, True)

        # Create header section at top of window
        header_frame = tk.Frame(self.window)
        # pack() adds the frame to window, fill="x" makes it stretch horizontally
        header_frame.pack(fill="x", padx=10, pady=5)

        # Create a title label for the agenda view
        header_label = tk.Label(
            header_frame,
            text="All Events - Agenda View",
            font=("Arial", 18, "bold")  # Large, bold font for title
        )
        # Add the label to the header frame
        header_label.pack()

        # Create a frame with border for the events section
        events_frame = tk.LabelFrame(self.window, text="All Events", font=("Arial", 12, "bold"))
        # fill="both" makes frame expand in all directions, expand=True allows it to grow
        events_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Create the treeview widget for displaying events in columns
        self.create_events_treeview(events_frame)

        # Create buttons at bottom for event management
        self.create_action_buttons()

        # Load and display all events
        self.refresh_events_display()

    def create_events_treeview(self, parent_frame):
        """
        Create a treeview widget to display events in a table format.
        
        Args:
            parent_frame (tk.LabelFrame): The frame to contain the treeview
        """
        # Create a frame to hold treeview and scrollbars
        tree_frame = tk.Frame(parent_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Define columns for the treeview (like a spreadsheet)
        columns = ("Date", "Time", "Title", "Description", "Recurring")
        
        # Create the treeview widget with defined columns
        # show="tree headings" shows both the tree structure and column headers
        self.events_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=20)

        # Configure each column with heading text and width
        self.events_tree.heading("Date", text="Date")
        self.events_tree.heading("Time", text="Time") 
        self.events_tree.heading("Title", text="Event Title")
        self.events_tree.heading("Description", text="Description")
        self.events_tree.heading("Recurring", text="Recurring")

        # Set column widths (in pixels)
        self.events_tree.column("Date", width=100, minwidth=80)
        self.events_tree.column("Time", width=120, minwidth=100)
        self.events_tree.column("Title", width=200, minwidth=150)
        self.events_tree.column("Description", width=250, minwidth=200)
        self.events_tree.column("Recurring", width=100, minwidth=80)

        # Create vertical scrollbar for when there are many events
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.events_tree.yview)
        # Connect scrollbar to treeview so they work together
        self.events_tree.configure(yscrollcommand=v_scrollbar.set)

        # Create horizontal scrollbar for when content is too wide
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.events_tree.xview)
        # Connect horizontal scrollbar to treeview
        self.events_tree.configure(xscrollcommand=h_scrollbar.set)

        # Pack the treeview and scrollbars using grid for better control
        self.events_tree.grid(row=0, column=0, sticky="nsew")  # nsew = north,south,east,west (fill all directions)
        v_scrollbar.grid(row=0, column=1, sticky="ns")         # ns = north,south (vertical only)
        h_scrollbar.grid(row=1, column=0, sticky="ew")         # ew = east,west (horizontal only)

        # Configure grid weights so treeview expands when window is resized
        tree_frame.grid_rowconfigure(0, weight=1)    # Row 0 (treeview) gets all extra vertical space
        tree_frame.grid_columnconfigure(0, weight=1) # Column 0 (treeview) gets all extra horizontal space

    def create_action_buttons(self):
        """Create buttons for event management actions."""
        # Create a horizontal container for all the buttons at bottom of window
        buttons_frame = tk.Frame(self.window)
        # fill="x" makes the frame stretch across the full width of window
        buttons_frame.pack(fill="x", padx=10, pady=5)

        # Create "Edit Selected Event" button with blue background
        edit_btn = tk.Button(
            buttons_frame,
            text="Edit Selected Event",              # Button label
            command=self.edit_selected_event,        # Function to call when clicked
            font=("Arial", 10),
            bg="lightblue"                           # Light blue background
        )
        # Pack on left side with some horizontal spacing
        edit_btn.pack(side="left", padx=5)

        # Create "Delete Selected Event" button with red background
        delete_btn = tk.Button(
            buttons_frame,
            text="Delete Selected Event",            # Button label
            command=self.delete_selected_event,      # Function to call when clicked
            font=("Arial", 10),
            bg="lightcoral"                          # Light red/pink background for warning
        )
        # Pack next to edit button on left side
        delete_btn.pack(side="left", padx=5)

        # Create "Refresh" button to reload all events
        refresh_btn = tk.Button(
            buttons_frame,
            text="Refresh",                          # Button label
            command=self.refresh_events_display,     # Function to call when clicked
            font=("Arial", 10),
            bg="lightgreen"                          # Light green background
        )
        # Pack next to other buttons on left side
        refresh_btn.pack(side="left", padx=5)

        # Create "Close" button with default color
        close_btn = tk.Button(
            buttons_frame,
            text="Close",
            command=self.window.destroy,             # Destroy (close) the window when clicked
            font=("Arial", 10)
        )
        # Pack on right side (opposite end from other buttons)
        close_btn.pack(side="right", padx=5)

    def refresh_events_display(self):
        """Refresh the events treeview with all current events."""
        # Clear the treeview completely (remove all existing items)
        # get_children() returns all items, delete() removes them
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)

        # Get all events from the calendar
        all_events = self.get_all_events()

        # Check if there are no events
        if not all_events:
            # Insert a message row to tell user there are no events
            self.events_tree.insert("", "end", values=("No events", "found", "", "", ""))
            return

        # Add each event as a row in the treeview
        # Events will be displayed in the order they exist in the calendar
        for event in all_events:
            # Format the date for display (convert from YYYY-MM-DD to readable format)
            try:
                # Parse the start date string and format it nicely
                date_obj = datetime.datetime.strptime(event.start_day, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%b %d, %Y")  # Example: "Nov 02, 2024"
            except ValueError:
                # If date parsing fails, just use the original date string
                formatted_date = event.start_day

            # Format the time display based on event type
            if event.is_all_day:
                time_display = "All Day"
            else:
                # Show start and end times
                time_display = f"{event.start_time} - {event.end_time}"

            # Format recurring status
            recurring_display = "Yes" if event.is_recurring else "No"
            if event.is_recurring and event.recurrence_pattern:
                recurring_display += f" ({event.recurrence_pattern})"

            # Truncate description if it's too long to fit nicely in the column
            description = event.description
            if len(description) > 50:  # Limit to 50 characters
                description = description[:47] + "..."  # Add ... to show it's truncated

            # Insert the event data as a new row in the treeview
            # "" means insert at root level, "end" means add to end of list
            # values is a tuple containing data for each column
            item_id = self.events_tree.insert("", "end", values=(
                formatted_date,      # Date column
                time_display,        # Time column
                event.title,         # Title column
                description,         # Description column
                recurring_display    # Recurring column
            ))

            # Store the actual event object with this treeview item
            # We'll use tags to store the event_id, which we can use to retrieve the event later
            self.events_tree.set(item_id, "event_id", event.event_id)

    def get_all_events(self):
        """
        Get all events from the calendar across all dates.
        
        Returns:
            list: List of all Event objects in the calendar
        """
        # Handle different calendar object types
        # MonthCalendar has a .calendar attribute that contains the actual Calendar object
        if hasattr(self.calendar, 'calendar') and hasattr(self.calendar.calendar, 'events'):
            # This is a MonthCalendar object
            calendar_obj = self.calendar.calendar
        elif hasattr(self.calendar, 'events'):
            # This is a Calendar object directly
            calendar_obj = self.calendar
        else:
            # Unknown calendar type
            return []

        # Get all events from the calendar's events dictionary
        # The events dictionary stores {event_id: Event_object}
        # We want just the Event objects, so we get the values
        if calendar_obj.events:
            return list(calendar_obj.events.values())
        else:
            # If no events dictionary or it's empty, return empty list
            return []

    def edit_selected_event(self):
        """Open edit dialog for the selected event."""
        # Get which item is currently selected in the treeview
        selected_items = self.events_tree.selection()
        
        # Check if user actually selected something
        if not selected_items:
            tk.messagebox.showwarning("No Selection", "Please select an event to edit.")
            return

        # Get the first selected item
        selected_item = selected_items[0]
        
        # Retrieve the event_id stored with this treeview item
        event_id = self.events_tree.set(selected_item, "event_id")
        
        # Check if this is a valid event (not the "No events found" message)
        if not event_id:
            tk.messagebox.showwarning("Invalid Selection", "Cannot edit this item.")
            return

        # Get the actual event object using the event_id
        # Handle different calendar object types
        if hasattr(self.calendar, 'calendar'):
            # This is a MonthCalendar object
            event_obj = self.calendar.calendar.get_event(event_id)
        else:
            # This is a Calendar object directly
            event_obj = self.calendar.get_event(event_id)
            
        if not event_obj:
            tk.messagebox.showerror("Error", "Event not found in calendar.")
            return

        # Import and create a DayViewGUI to handle the editing
        # We'll use the event's date to create the day view
        try:
            from DayViewGUI_Class import DayViewGUI
            
            # Parse the event date to get year, month, day
            date_obj = datetime.datetime.strptime(event_obj.start_day, "%Y-%m-%d")
            
            # Create a day view for this event's date
            # The day view has the event editing functionality we need
            day_view = DayViewGUI(
                self.calendar, 
                date_obj.year, 
                date_obj.month, 
                date_obj.day, 
                self.parent_gui
            )
            
            # Find the event in the day view's event list and trigger edit
            day_view.refresh_events_list()
            for i, day_event in enumerate(day_view.current_events):
                if day_event.event_id == event_obj.event_id:
                    # Found the matching event, open edit dialog
                    day_view.event_form_dialog("Edit Event", i)
                    break
                    
        except ImportError:
            tk.messagebox.showerror("Error", "Cannot import DayViewGUI class for editing.")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to edit event: {str(e)}")

    def delete_selected_event(self):
        """Delete the selected event after confirmation."""
        # Get which item is currently selected in the treeview
        selected_items = self.events_tree.selection()
        
        # Check if user actually selected something
        if not selected_items:
            tk.messagebox.showwarning("No Selection", "Please select an event to delete.")
            return

        # Get the first selected item
        selected_item = selected_items[0]
        
        # Retrieve the event_id stored with this treeview item  
        event_id = self.events_tree.set(selected_item, "event_id")
        
        # Check if this is a valid event (not the "No events found" message)
        if not event_id:
            tk.messagebox.showwarning("Invalid Selection", "Cannot delete this item.")
            return

        # Get the actual event object using the event_id  
        # Handle different calendar object types
        if hasattr(self.calendar, 'calendar'):
            # This is a MonthCalendar object
            event_obj = self.calendar.calendar.get_event(event_id)
        else:
            # This is a Calendar object directly
            event_obj = self.calendar.get_event(event_id)
            
        if not event_obj:
            tk.messagebox.showerror("Error", "Event not found in calendar.")
            return

        # Show confirmation dialog before deleting (prevent accidental deletions)
        # askyesno() returns True if user clicks "Yes", False if "No"
        confirm = tk.messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the event '{event_obj.title}'?"
        )

        # Only proceed if user confirmed they want to delete
        if confirm:
            # Call the calendar's delete method to remove event from database
            success = self.calendar.delete_event(event_obj.event_id)

            # Check if the deletion was successful
            if success:
                # Refresh this agenda view to remove the deleted event from the list
                self.refresh_events_display()
                
                # If there's a parent month view window, refresh it too
                # This updates the month calendar to remove the event indicator
                if self.parent_gui:
                    self.parent_gui.refresh_calendar_display()
                    
                # Show success message to user
                tk.messagebox.showinfo("Success", "Event deleted successfully.")
            else:
                # Show error message if deletion failed
                tk.messagebox.showerror("Error", "Failed to delete event.")