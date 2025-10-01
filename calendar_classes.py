"""
To Include/Think about

- Let user choose what month it is
- Specify what a whole month is - Done
- The object should include a list of events
- Click on day then display a list of events
- Buttons for calendar days
- Start day, end Day
- Use calendar class to store data

TODOList
- add buttons to empty days
- Update Calendar Class
- Make day of week buttons non clickable
- add docStrings for classes and methods
-connect calendar class to monthViewGUI class
"""

import tkinter as tk
import datetime
import calendar


class Calendar(object):
    def __init__(self):
        self.current_month = datetime.date.month()
        self.current_date = datetime.date.today()
        self.events = {} # title as the keys, and the values as the dates

    def add_event(self, event_id, title, date, start_time, end_time, description, is_recurring):
        # create an Event object
        new_event = Event(event_id, title, date, start_time, end_time, description, is_recurring)

        # store it in events dictionary
        self.events[new_event.event_id] = date #changed dictionary key to event id


    def get_event(self, title):
        if title in self.events:
            return self.events[title]
        else:
            return None

    def update_event(self, date, event_id, new_title=None, new_start=None, new_end=None, new_desc=None, new_recurring=None):
        if date in self.events:
            for event in self.events[date]:
                if event.event_id == event_id:
                    if new_title is not None:
                        event.title = new_title
                    if new_start is not None:
                        event.start_time = new_start
                    if new_end is not None:
                        event.end_time = new_end
                    if new_desc is not None:
                        event.description = new_desc
                    if new_recurring is not None:
                        event.is_recurring = new_recurring

    def delete_event(self, title):
        if title in self.events:
            del self.events[title]

    def get_month_view(self):

        pass


class MonthViewGUI():
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Month View Calendar")
        self.today = datetime.date.today()
        self.current_month = self.today.month
        self.current_year = self.today.year
        self.showing_next = False

        self.header = tk.Label(self.window, font=("Arial", 16, "bold"))
        self.header.grid(row=0, column=0, columnspan=7)

        self.switch_btn = tk.Button(self.window, text="Show Next Month", command=self.switch_month)
        self.switch_btn.grid(row=1, column=0, columnspan=7)

        self.frame = tk.Frame(self.window)
        self.frame.grid(row=2, column=0, columnspan=7)

        self.show_month(self.current_year, self.current_month)
        self.window.mainloop()

    def switch_month(self):
        self.showing_next = not self.showing_next
        if self.showing_next:
            if self.current_month < 12:
                year, month = self.current_year, self.current_month + 1
            else:
                year, month = self.current_year + 1, 1
            self.switch_btn.config(text="Show This Month")
        else:
            year, month = self.current_year, self.current_month
            self.switch_btn.config(text="Show Next Month")
        self.show_month(year, month)

    def show_month(self, year, month):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.header.config(text=f"{calendar.month_name[month]} {year}")

        days_of_the_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        col = 0
        while col < 7:
            tk.Button(self.frame, text=days_of_the_week[col], width=10, height=2).grid(row=0, column=col)
            col += 1

        first_weekday, num_days = calendar.monthrange(year, month)
        # Adjust so Sunday is column 0
        col = (first_weekday + 1) % 7
        day_num = 1
        row = 1
        while day_num <= num_days:
            if (year, month, day_num) == (self.today.year, self.today.month, self.today.day):
                fg = "red"
            else:
                fg = "black"
            tk.Button(self.frame, text=day_num, anchor="ne", width=10, height=7, fg=fg).grid(row=row, column=col)
            day_num += 1
            col += 1
            if col > 6:
                col = 0
                row += 1

class Event(object):
    def __init__(self, event_id:str, title:str, date:str, start_day, end_day, start_time:str, end_time:str, description:str, is_recurring:bool):
        self.event_id = event_id
        self.title = title
        self.date = date # Added the date attribute
        self.start_day: start_day #Added start day
        self.end_time: end_day #Added end day
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.is_recurring = is_recurring


MonthViewGUI()


# Added: self.window.title("Month View Calendar") to set the window title.
# Added: self.today = datetime.date.today() to track today's date.
# Added: self.current_month and self.current_year to store the current month and year.
# Added: self.showing_next to track which month is displayed.
# Added: self.header label to display the month and year.
# Added: self.switch_btn button to toggle between current and next month.
# Added: self.frame to contain the calendar grid.
# Replaced: static month display with self.show_month(self.current_year, self.current_month).
# Added: switch_month method to handle toggling between months.
# Added: show_month method to dynamically display the correct month and highlight today's date.
# Changed: Days of the week are displayed using a while loop instead of a for loop.
# Changed: Calculation of the starting column for the first day using col = (first_weekday + 1) % 7 for correct alignment.
# Changed: Day buttons are created in a while loop, with today's date highlighted in red.
# Removed: monthsOfYear dictionary and static button creation for days.
# Removed: static for loops for days and weeks; replaced with dynamic month rendering.