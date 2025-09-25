"""
To Include/Think about
- Let user choose what month it is
- Specify what a whole month is
- The object should include a list of events
- Click on day then display a list of events
- Buttons for calendar days
- Start day, end Day

"""
"""
TODO
- Connect days of the month to days of the week
- Finish Calendar Class
- Create a GUI for creating a Calendar
"""
import tkinter as tk
import datetime
class Calendar(object):
    def __init__(self, month, day, year, dayOfWeek, events):
        self.month = month
        self.day = day
        self.year = year
        self.dayOfWeek = dayOfWeek
        self.event = []


class MonthViewGUI():
    def __init__(self):
        self.window = tk.Tk()
        root = self.window
        self.monthsOfYear = {"January":31, "February":28, "March":31, "April":30,
                             "May":31, "June":30, "July":31, "August":31,
                             "September":30, "October":31, "November":30, "December":31}

        #Displays the days of the week
        days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        for col in range(7):
            tk.Button(root, text=days_of_the_week[col], width=10, height=2).grid(row=0, column=col)
        numOfDays = 1

        #Displays a button for each day of the month
        for row in range(5):
            for col in range(7):
                tk.Button(root, text=numOfDays, anchor="ne",width=10,height=7).grid(row = row+1, column = col)
                numOfDays += 1
        root.mainloop()


MonthViewGUI()