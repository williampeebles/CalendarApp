"""
- Let user choose what month it is
- Specify what a whole month is
- The object should include a list of events
- Click on day then display a list of events
- Buttons for calendar days
- Start day, end Day

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
        self.window.mainloop()





MonthViewGUI()