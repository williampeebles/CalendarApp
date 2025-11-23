"""
Unit tests for FilterService class.

Tests event filtering and validation functionality.
"""

import unittest
import datetime

# Import the classes we need to test
from CalendarService import CalendarService
from Calendar_Database_Class import CalendarDatabase
from Filter_Service_Class import FilterService
from Event_Class import Event


class TestFilterService(unittest.TestCase):
    """Test FilterService functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_db_path = "test_filter.db"
        
        self.db = CalendarDatabase(self.test_db_path)
        self.calendar_service = CalendarService(self.db)
        self.filter_service = FilterService()
        
        # Create various test events
        base_date = datetime.date.today() + datetime.timedelta(days=1)
        
        # All-day event
        self.calendar_service.create_event(
            title="Morning Meeting",
            date=base_date,
            is_all_day=True
        )
        
        # Timed event
        self.calendar_service.create_event(
            title="Afternoon Session",
            date=base_date + datetime.timedelta(days=1),
            start_time="02:00 PM",
            end_time="03:00 PM",
            description="Important meeting"
        )
        
        # Another event for later
        self.calendar_service.create_event(
            title="Evening Event",
            date=base_date + datetime.timedelta(days=5),
            start_time="06:00 PM",
            end_time="07:00 PM"
        )

    def tearDown(self):
        """Clean up after each test"""
        pass

    def _get_all_events(self):
        """Helper method to get all events from database"""
        all_events = []
        today = datetime.date.today()
        for i in range(10):
            date = today + datetime.timedelta(days=i)
            events = self.calendar_service.repository.get_events_for_date(
                date.strftime("%Y-%m-%d")
            )
            for event_dict in events:
                all_events.append(Event.from_dict(event_dict))
        return all_events

    def test_filter_by_text(self):
        """Test filtering events by text search"""
        all_events = self._get_all_events()
        
        # Filter for "morning"
        criteria = {
            'search_text': 'morning',
            'from_date': None,
            'to_date': None,
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': True
        }
        
        filtered = self.filter_service.filter_events(all_events, criteria)
        
        self.assertGreater(len(filtered), 0)
        for event in filtered:
            self.assertIn('morning', event.title.lower())

    def test_filter_by_text_case_insensitive(self):
        """Test that text filtering is case-insensitive"""
        all_events = self._get_all_events()
        
        criteria = {
            'search_text': 'EVENING',
            'from_date': None,
            'to_date': None,
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': True
        }
        
        filtered = self.filter_service.filter_events(all_events, criteria)
        
        self.assertGreater(len(filtered), 0)

    def test_filter_by_date_range(self):
        """Test filtering events by date range"""
        base_date = datetime.date.today() + datetime.timedelta(days=1)
        all_events = self._get_all_events()
        
        # Filter for first 3 days only
        criteria = {
            'search_text': '',
            'from_date': base_date,
            'to_date': base_date + datetime.timedelta(days=2),
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': True
        }
        
        filtered = self.filter_service.filter_events(all_events, criteria)
        
        # Should only have events from first 3 days
        self.assertLessEqual(len(filtered), 2)

    def test_filter_by_event_type_all_day_only(self):
        """Test filtering for only all-day events"""
        all_events = self._get_all_events()
        
        # Filter for only all-day events
        criteria = {
            'search_text': '',
            'from_date': None,
            'to_date': None,
            'show_all_day': True,
            'show_timed': False,
            'show_recurring': True
        }
        
        filtered = self.filter_service.filter_events(all_events, criteria)
        
        # All filtered events should be all-day
        for event in filtered:
            self.assertTrue(event.is_all_day)

    def test_filter_by_event_type_timed_only(self):
        """Test filtering for only timed events"""
        all_events = self._get_all_events()
        
        # Filter for only timed events
        criteria = {
            'search_text': '',
            'from_date': None,
            'to_date': None,
            'show_all_day': False,
            'show_timed': True,
            'show_recurring': True
        }
        
        filtered = self.filter_service.filter_events(all_events, criteria)
        
        # All filtered events should NOT be all-day
        for event in filtered:
            self.assertFalse(event.is_all_day)

    def test_filter_with_no_criteria(self):
        """Test that filtering with None criteria returns all events"""
        all_events = self._get_all_events()
        
        filtered = self.filter_service.filter_events(all_events, None)
        
        self.assertEqual(len(filtered), len(all_events))

    def test_filter_empty_search_text(self):
        """Test filtering with empty search text returns all events"""
        all_events = self._get_all_events()
        
        criteria = {
            'search_text': '',
            'from_date': None,
            'to_date': None,
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': True
        }
        
        filtered = self.filter_service.filter_events(all_events, criteria)
        
        self.assertEqual(len(filtered), len(all_events))

    def test_validate_filter_criteria_valid(self):
        """Test validation passes for valid criteria"""
        criteria = {
            'from_date': datetime.date(2025, 11, 1),
            'to_date': datetime.date(2025, 11, 30),
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': True
        }
        
        errors = self.filter_service.validate_filter_criteria(criteria)
        
        self.assertEqual(len(errors), 0)

    def test_validate_filter_criteria_invalid_date_range(self):
        """Test validation catches invalid date ranges"""
        criteria = {
            'from_date': datetime.date(2025, 12, 1),
            'to_date': datetime.date(2025, 11, 1),  # Before from_date!
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': True
        }
        
        errors = self.filter_service.validate_filter_criteria(criteria)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('date' in error.lower() for error in errors))

    def test_validate_filter_criteria_no_types_selected(self):
        """Test validation catches when no event types are selected"""
        criteria = {
            'from_date': None,
            'to_date': None,
            'show_all_day': False,
            'show_timed': False,
            'show_recurring': False
        }
        
        errors = self.filter_service.validate_filter_criteria(criteria)
        
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('type' in error.lower() for error in errors))

    def test_get_filter_summary(self):
        """Test generating human-readable filter summary"""
        criteria = {
            'search_text': 'meeting',
            'from_date': datetime.date(2025, 11, 1),
            'to_date': datetime.date(2025, 11, 30),
            'show_all_day': True,
            'show_timed': True,
            'show_recurring': False
        }
        
        summary = self.filter_service.get_filter_summary(criteria)
        
        self.assertIn('meeting', summary.lower())
        self.assertIn('01-11-2025', summary)
        self.assertIn('30-11-2025', summary)
        self.assertIn('recurring', summary.lower())

    def test_get_filter_summary_no_filters(self):
        """Test filter summary with no filters applied"""
        summary = self.filter_service.get_filter_summary(None)
        
        self.assertIn("no filter", summary.lower())


if __name__ == "__main__":
    unittest.main()
