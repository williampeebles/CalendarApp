"""
To Include/Think about
- Let user choose what month it is,
(May implement later, allowing user to see months up to 6-months).
*******************************************************************************
TODOList
✓ Character limit on description (80 characters with live counter)
✓ When creating an event, if a user selects a start day after the current date,
  then that event should be applied to that selected day
✓ No need for 11-parameter for one method (Reduced to 4 parameters with dataclass)
- Refractor
✓ Configuration file for that database class-recurring events applied to calendar
✓ The event class should be the class responsible for creating event objects.
  (Event.from_dict() and Event.create_new() factory methods implemented)

"""
from CalendarService import CalendarService
from MonthViewGUI_Class import MonthViewGUI


def main():
    # Create calendar service instance
    calendar = CalendarService()
    print("Calendar application started!")
    print("Calendar instance created successfully.")

    # Launch the GUI
    print("Starting calendar GUI...")
    gui = MonthViewGUI(calendar)


if __name__ == "__main__":
    main()
