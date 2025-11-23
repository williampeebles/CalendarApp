"""
Unit tests for AgendaViewService class.

Tests agenda-specific operations including multi-date event retrieval.
"""

import unittest
import datetime

# Import the classes we need to test
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase
from AgendaViewService_Class import AgendaViewService


class TestAgendaViewService(unittest.TestCase):
    """Test AgendaViewService functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "test_agenda.db"
        
        self.db = CalendarDatabase(self.test_db_path)
        self.calendar_service = CalendarService(self.db)
        self.agenda_service = AgendaViewService(self.calendar_service)
        
        # Create multiple test events
        for i in range(3):
            future_date = datetime.date.today() + datetime.timedelta(days=i+1)
            self.calendar_service.create_event(
                title=f"Event {i+1}",
                date=future_date,
                start_time="10:00 AM",
                end_time="11:00 AM"
            )

    def tearDown(self):
        """Clean up after each test"""
        pass

    def test_get_all_events(self):
        """Test getting all events"""
        events = self.agenda_service.get_all_events()
        
        self.assertIsInstance(events, list)
        self.assertGreaterEqual(len(events), 3)  # Should have our 3 test events

    def test_get_all_events_sorted(self):
        """Test that events are sorted by date and time"""
        events = self.agenda_service.get_all_events()
        
        # Check that events are in chronological order
        for i in range(len(events) - 1):
            current = events[i]
            next_event = events[i + 1]
            # Compare dates (and times if same date)
            self.assertLessEqual((current.date, current.start_time), 
                                (next_event.date, next_event.start_time))

    def test_get_all_events_with_custom_range(self):
        """Test getting events with custom month range"""
        # Get events for smaller range
        events = self.agenda_service.get_all_events(months_before=1, months_after=1)
        
        self.assertIsInstance(events, list)

    def test_get_event_by_id(self):
        """Test getting a specific event by ID"""
        # Get all events
        events = self.agenda_service.get_all_events()
        
        if events:
            first_event = events[0]
            # Get the same event by ID
            retrieved_event = self.agenda_service.get_event_by_id(first_event.event_id)
            
            self.assertIsNotNone(retrieved_event)
            self.assertEqual(retrieved_event.event_id, first_event.event_id)
            self.assertEqual(retrieved_event.title, first_event.title)

    def test_get_event_by_invalid_id(self):
        """Test getting event with invalid ID returns None"""
        result = self.agenda_service.get_event_by_id(99999)
        self.assertIsNone(result)

    def test_delete_event_through_agenda_service(self):
        """Test deleting event through AgendaViewService"""
        # Get an event
        events = self.agenda_service.get_all_events()
        self.assertGreater(len(events), 0)
        
        event_to_delete = events[0]
        
        # Delete it
        success, message = self.agenda_service.delete_event(event_to_delete.event_id)
        
        self.assertTrue(success)
        self.assertIn("deleted", message.lower())
        
        # Verify it's gone
        deleted_event = self.agenda_service.get_event_by_id(event_to_delete.event_id)
        self.assertIsNone(deleted_event)

    def test_get_all_events_empty_calendar(self):
        """Test getting events from empty calendar"""
        # Create a new empty database
        empty_db_path = "test_empty_agenda.db"
        
        empty_db = CalendarDatabase(empty_db_path)
        empty_service = CalendarService(empty_db)
        empty_agenda = AgendaViewService(empty_service)
        
        events = empty_agenda.get_all_events()
        
        self.assertIsInstance(events, list)
        self.assertEqual(len(events), 0)


if __name__ == "__main__":
    unittest.main()
