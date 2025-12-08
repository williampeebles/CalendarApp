
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
