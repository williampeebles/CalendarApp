"""
To Include/Think about
- Let user choose what month it is,
(May implement later, allowing user to see months up to 6-months).
*******************************************************************************
TODOList
- Character limit on description
- When creating an event, if a user selects a start day after the current date,
  then that event should be applied to that selected day
- No need for 11-parameter for one method
- Refractor
- Configuration file for that database class-recurring events applied to calendar
- The event class should be the class responsible for creating event objects.
-Method that are only created to call other methods should be removed.
The calendar class should s
The database should only store and retrieve event objects, the program should not be directly

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
