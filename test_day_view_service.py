"""
Unit tests for DayViewService class.

Tests day-specific operations including event CRUD operations.
"""

import unittest
import datetime

# Import the classes we need to test
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase
from DayViewService_Class import DayViewService


class TestDayViewService(unittest.TestCase):
    """Test DayViewService functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "test_day.db"
        
        self.db = CalendarDatabase(self.test_db_path)
        self.calendar_service = CalendarService(self.db)
        self.day_service = DayViewService(self.calendar_service)

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_format_date_for_display(self):
        """Test date formatting for display (DD-MM-YYYY)"""
        test_date = datetime.date(2025, 11, 17)
        result = self.day_service.format_date_for_display(test_date)
        self.assertEqual(result, "17-11-2025")

    def test_format_date_with_single_digits(self):
        """Test date formatting with single digit month/day"""
        test_date = datetime.date(2025, 1, 5)
        result = self.day_service.format_date_for_display(test_date)
        self.assertEqual(result, "05-01-2025")

    def test_get_events_for_date_empty(self):
        """Test getting events for date with no events"""
        future_date = datetime.date.today() + datetime.timedelta(days=50)
        events = self.day_service.get_events_for_date(future_date)
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 0)

    def test_get_events_for_date_with_events(self):
        """Test getting events for a specific date"""
        future_date = datetime.date.today() + datetime.timedelta(days=10)
        
        # Create an event
        self.day_service.create_event(
            title="Day Test Event",
            date=future_date,
            start_time="03:00 PM",
            end_time="04:00 PM"
        )
        
        # Get events for that date
        events = self.day_service.get_events_for_date(future_date)
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].title, "Day Test Event")

    def test_create_event_through_day_service(self):
        """Test creating event through DayViewService"""
        future_date = datetime.date.today() + datetime.timedelta(days=7)
        
        success, message, event_id = self.day_service.create_event(
            title="Service Test",
            date=future_date,
            start_time="11:00 AM",
            end_time="12:00 PM",
            description="Test description"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(event_id)
        self.assertGreater(event_id, 0)

    def test_update_event_through_day_service(self):
        """Test updating event through DayViewService"""
        future_date = datetime.date.today() + datetime.timedelta(days=4)
        
        # Create event
        success, message, event_id = self.day_service.create_event(
            title="Original",
            date=future_date,
            start_time="09:00 AM",
            end_time="10:00 AM"
        )
        self.assertTrue(success)
        
        # Update it
        success, message = self.day_service.update_event(
            event_id,
            title="Updated Title"
        )
        
        self.assertTrue(success)
        self.assertIn("updated", message.lower())

    def test_delete_event_through_day_service(self):
        """Test deleting event through DayViewService"""
        future_date = datetime.date.today() + datetime.timedelta(days=3)
        
        # Create event
        success, message, event_id = self.day_service.create_event(
            title="To Delete",
            date=future_date,
            start_time="02:00 PM",
            end_time="03:00 PM"
        )
        self.assertTrue(success)
        
        # Delete it
        success, message = self.day_service.delete_event(event_id)
        
        self.assertTrue(success)
        self.assertIn("deleted", message.lower())

    def test_create_all_day_event(self):
        """Test creating all-day event through DayViewService"""
        future_date = datetime.date.today() + datetime.timedelta(days=6)
        
        success, message, event_id = self.day_service.create_event(
            title="All Day Meeting",
            date=future_date,
            is_all_day=True
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(event_id)


if __name__ == "__main__":
    unittest.main()
