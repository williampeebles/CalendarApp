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
"""
from Calendar_Class import Calendar
from MonthViewGUI_Class import MonthViewGUI


def main():
    # Create calendar instance
    calendar = Calendar()
    print("Calendar application started!")
    print("Calendar instance created successfully.")

    # Launch the GUI
    print("Starting calendar GUI...")
    gui = MonthViewGUI(calendar)


if __name__ == "__main__":
    main()
