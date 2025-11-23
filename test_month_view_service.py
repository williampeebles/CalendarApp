"""
Unit tests for MonthViewService class.

Tests month-specific operations including navigation and event retrieval.
"""

import unittest
import datetime

# Import the classes we need to test
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase
from MonthViewService_Class import MonthViewService


class TestMonthViewService(unittest.TestCase):
    """Test MonthViewService functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "test_month.db"
        
        self.db = CalendarDatabase(self.test_db_path)
        self.calendar_service = CalendarService(self.db)
        self.month_service = MonthViewService(self.calendar_service)
        
        # Create some test events
        future_date = datetime.date.today() + datetime.timedelta(days=5)
        self.calendar_service.create_event(
            title="Test Event",
            date=future_date,
            start_time="10:00 AM",
            end_time="11:00 AM"
        )

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_get_current_month_year(self):
        """Test getting current month and year"""
        month, year = self.month_service.get_current_month_year()
        today = datetime.date.today()
        self.assertEqual(month, today.month)
        self.assertEqual(year, today.year)

    def test_calculate_next_month(self):
        """Test calculating next month"""
        year, month = self.month_service.calculate_next_month(2025, 11)
        self.assertEqual(year, 2025)
        self.assertEqual(month, 12)
        
        # Test year boundary
        year, month = self.month_service.calculate_next_month(2025, 12)
        self.assertEqual(year, 2026)
        self.assertEqual(month, 1)

    def test_calculate_previous_month(self):
        """Test calculating previous month"""
        year, month = self.month_service.calculate_previous_month(2025, 11)
        self.assertEqual(year, 2025)
        self.assertEqual(month, 10)
        
        # Test year boundary
        year, month = self.month_service.calculate_previous_month(2025, 1)
        self.assertEqual(year, 2024)
        self.assertEqual(month, 12)

    def test_format_month_display_name(self):
        """Test formatting month display name"""
        result = self.month_service.format_month_display_name(2025, 11)
        self.assertEqual(result, "November 2025")

    def test_has_events_on_date(self):
        """Test checking if date has events"""
        # Date with event
        future_date = datetime.date.today() + datetime.timedelta(days=5)
        self.assertTrue(self.month_service.has_events_on_date(future_date))
        
        # Date without event
        other_date = datetime.date.today() + datetime.timedelta(days=100)
        self.assertFalse(self.month_service.has_events_on_date(other_date))

    def test_get_events_for_month(self):
        """Test getting events for a specific month"""
        today = datetime.date.today()
        events = self.month_service.get_events_for_month(today.year, today.month)
        
        self.assertIsInstance(events, list)
        # Should have at least our test event
        self.assertGreaterEqual(len(events), 1)

    def test_get_events_for_date(self):
        """Test getting events for a specific date"""
        future_date = datetime.date.today() + datetime.timedelta(days=5)
        events = self.month_service.get_events_for_date(future_date)
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "Test Event")

    def test_get_events_for_all_months(self):
        """Test getting events across multiple months"""
        events = self.month_service.get_events_for_all_months()
        
        self.assertIsInstance(events, list)
        self.assertGreaterEqual(len(events), 1)


if __name__ == "__main__":
    unittest.main()
