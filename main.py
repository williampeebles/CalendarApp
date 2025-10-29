"""
To Include/Think about
- Let user choose what month it is,
(May implement later, allowing user to see months up to 6-months).
*******************************************************************************
TODOList
- Character limit on description
-When creating an event, if user selects a start day that is after the current date,
then that event should be applied to that selected day
- Instead of opening a new window for switching to week view, just change the current window's view.
-Add Agenda view
Add properties to event class (getter and setter methods) Add more comments
No need for 11 parameters
Refractor and no inner methods.


"""
from Calendar_Class import Calendar
from MonthViewGUI_Class import MonthViewGUI

# Create a calendar instance and start the GUI
calendar_app = Calendar()
MonthViewGUI(calendar_app)