"""
Unit tests for CalendarService class.

Tests core calendar functionality including event creation, updating, and deletion.
"""

import unittest
import datetime

# Import the classes we need to test
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase


class TestCalendarService(unittest.TestCase):
    """Test core CalendarService functionality"""

    def setUp(self):
        """Set up test fixtures with a real in-memory database"""
        # Create a temporary database for testing
        self.test_db_path = "test_calendar.db"
        
        # Create real instances
        self.db = CalendarDatabase(self.test_db_path)
        self.service = CalendarService(self.db)

    def tearDown(self):
        """Clean up after each test"""
        # Database cleanup happens automatically
        pass

    # === Core Functionality Tests ===

    def test_get_today(self):
        """Test that get_today returns today's date"""
        result = self.service.get_today()
        self.assertEqual(result, datetime.date.today())
        self.assertIsInstance(result, datetime.date)

    def test_create_event_success(self):
        """Test creating a valid event"""
        future_date = datetime.date.today() + datetime.timedelta(days=7)
        
        success, message, event_id = self.service.create_event(
            title="Test Event",
            date=future_date,
            start_time="10:00 AM",
            end_time="11:00 AM",
            description="Test description"
        )
        
        self.assertTrue(success)
        self.assertIn("successfully", message.lower())
        self.assertIsNotNone(event_id)
        self.assertGreater(event_id, 0)

    def test_create_event_with_empty_title(self):
        """Test that creating event with empty title fails"""
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        
        success, message, event_id = self.service.create_event(
            title="",
            date=future_date,
            start_time="10:00 AM",
            end_time="11:00 AM"
        )
        
        self.assertFalse(success)
        self.assertIn("title", message.lower())
        self.assertIsNone(event_id)

    def test_create_event_past_date(self):
        """Test that creating event in the past fails"""
        past_date = datetime.date.today() - datetime.timedelta(days=1)
        
        success, message, event_id = self.service.create_event(
            title="Past Event",
            date=past_date,
            start_time="10:00 AM",
            end_time="11:00 AM"
        )
        
        self.assertFalse(success)
        self.assertIn("past", message.lower())
        self.assertIsNone(event_id)

    def test_create_all_day_event(self):
        """Test creating an all-day event"""
        future_date = datetime.date.today() + datetime.timedelta(days=3)
        
        success, message, event_id = self.service.create_event(
            title="All Day Event",
            date=future_date,
            is_all_day=True
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(event_id)

    def test_update_event(self):
        """Test updating an existing event"""
        # First create an event
        future_date = datetime.date.today() + datetime.timedelta(days=5)
        success, message, event_id = self.service.create_event(
            title="Original Title",
            date=future_date,
            start_time="09:00 AM",
            end_time="10:00 AM"
        )
        self.assertTrue(success)
        
        # Now update it
        success, message = self.service.update_event(
            event_id,
            title="Updated Title",
            description="New description"
        )
        
        self.assertTrue(success)
        self.assertIn("updated", message.lower())

    def test_delete_event(self):
        """Test deleting an event"""
        # Create an event
        future_date = datetime.date.today() + datetime.timedelta(days=2)
        success, message, event_id = self.service.create_event(
            title="Event to Delete",
            date=future_date,
            start_time="10:00 AM",
            end_time="11:00 AM"
        )
        self.assertTrue(success)
        
        # Delete it
        success, message = self.service.delete_event(event_id)
        
        self.assertTrue(success)
        self.assertIn("deleted", message.lower())

    def test_create_recurring_event(self):
        """Test creating a recurring event"""
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        
        success, message, event_id = self.service.create_event(
            title="Weekly Meeting",
            date=future_date,
            start_time="02:00 PM",
            end_time="03:00 PM",
            is_recurring=True,
            recurrence_pattern="weekly"
        )
        
        self.assertTrue(success)
        self.assertIn("recurring", message.lower())
        self.assertIsNotNone(event_id)

    def test_description_length_validation(self):
        """Test that description over 80 characters is rejected"""
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        long_description = "A" * 81  # 81 characters
        
        success, message, event_id = self.service.create_event(
            title="Test Event",
            date=future_date,
            start_time="10:00 AM",
            end_time="11:00 AM",
            description=long_description
        )
        
        self.assertFalse(success)
        self.assertIn("80", message)
        self.assertIn("character", message.lower())


if __name__ == "__main__":
    unittest.main()
