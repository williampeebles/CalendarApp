"""
Unit tests for WeekViewService class.

Tests week-specific operations including week calculations and formatting.
"""

import unittest
import datetime

# Import the classes we need to test
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase
from WeekViewService_Class import WeekViewService


class TestWeekViewService(unittest.TestCase):
    """Test WeekViewService functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "test_week.db"
        
        self.db = CalendarDatabase(self.test_db_path)
        self.calendar_service = CalendarService(self.db)
        self.week_service = WeekViewService(self.calendar_service)

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_calculate_week_start(self):
        """Test calculating week start (Sunday)"""
        # November 17, 2025 is a Monday
        test_date = datetime.date(2025, 11, 17)
        week_start = self.week_service.calculate_week_start(test_date)
        
        # Should return the previous Sunday (November 16)
        self.assertEqual(week_start, datetime.date(2025, 11, 16))
        self.assertEqual(week_start.weekday(), 6)  # Sunday is weekday 6

    def test_calculate_week_start_for_sunday(self):
        """Test that Sunday returns itself as week start"""
        test_date = datetime.date(2025, 11, 16)  # Sunday
        week_start = self.week_service.calculate_week_start(test_date)
        
        self.assertEqual(week_start, test_date)

    def test_calculate_week_dates(self):
        """Test calculating all 7 dates in a week"""
        week_start = datetime.date(2025, 11, 16)  # Sunday
        week_dates = self.week_service.calculate_week_dates(week_start)
        
        self.assertEqual(len(week_dates), 7)
        self.assertEqual(week_dates[0], datetime.date(2025, 11, 16))  # Sunday
        self.assertEqual(week_dates[6], datetime.date(2025, 11, 22))  # Saturday

    def test_format_week_display_name_same_month(self):
        """Test formatting week display name within same month"""
        week_start = datetime.date(2025, 11, 16)  # Sunday
        week_end = datetime.date(2025, 11, 22)    # Saturday
        
        result = self.week_service.format_week_display_name(week_start, week_end)
        
        self.assertIn("November", result)
        self.assertIn("16", result)
        self.assertIn("22", result)
        self.assertIn("2025", result)

    def test_format_week_display_name_cross_month(self):
        """Test formatting week display name across months"""
        week_start = datetime.date(2025, 11, 30)  # Sunday in November
        week_end = datetime.date(2025, 12, 6)     # Saturday in December
        
        result = self.week_service.format_week_display_name(week_start, week_end)
        
        self.assertIn("November", result)
        self.assertIn("December", result)

    def test_has_events_on_date(self):
        """Test checking if date has events"""
        # Create an event
        future_date = datetime.date.today() + datetime.timedelta(days=10)
        self.calendar_service.create_event(
            title="Week Test Event",
            date=future_date,
            start_time="10:00 AM",
            end_time="11:00 AM"
        )
        
        # Check date with event
        self.assertTrue(self.week_service.has_events_on_date(future_date))
        
        # Check date without event
        other_date = datetime.date.today() + datetime.timedelta(days=100)
        self.assertFalse(self.week_service.has_events_on_date(other_date))

    def test_get_events_for_date(self):
        """Test getting events for a specific date"""
        future_date = datetime.date.today() + datetime.timedelta(days=8)
        
        # Create an event
        self.calendar_service.create_event(
            title="Daily Event",
            date=future_date,
            start_time="03:00 PM",
            end_time="04:00 PM"
        )
        
        # Get events for that date
        events = self.week_service.get_events_for_date(future_date)
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "Daily Event")


if __name__ == "__main__":
    unittest.main()
