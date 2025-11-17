import unittest
import datetime
from CalendarService import CalendarService


class TestCalendarService(unittest.TestCase):
    """Test for CalendarService class"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.service = CalendarService()
        self.today = datetime.date.today()

    # === Date Utility Tests ===

    def test_get_today(self):
        """Test that get_today returns today's date"""
        result = self.service.get_today()
        self.assertEqual(result, datetime.date.today())
        self.assertIsInstance(result, datetime.date)

    def test_format_date_for_display(self):
        """Test date formatting for display (DD-MM-YYYY)"""
        test_date = datetime.date(2025, 11, 17)
        result = self.service.format_date_for_display(test_date)
        self.assertEqual(result, "17-11-2025")

    def test_calculate_next_month(self):
        """Test calculating next month"""
        year, month = self.service.calculate_next_month(2025, 11)
        self.assertEqual(year, 2025)
        self.assertEqual(month, 12)
        
        # Test year boundary
        year, month = self.service.calculate_next_month(2025, 12)
        self.assertEqual(year, 2026)
        self.assertEqual(month, 1)

    def test_calculate_previous_month(self):
        """Test calculating previous month"""
        year, month = self.service.calculate_previous_month(2025, 11)
        self.assertEqual(year, 2025)
        self.assertEqual(month, 10)
        
        # Test year boundary
        year, month = self.service.calculate_previous_month(2025, 1)
        self.assertEqual(year, 2024)
        self.assertEqual(month, 12)

    def test_calculate_week_start(self):
        """Test calculating week start (Sunday)"""
        # November 17, 2025 is a Monday
        test_date = datetime.date(2025, 11, 17)
        week_start = self.service.calculate_week_start(test_date)
        # Should return the previous Sunday (November 16)
        self.assertEqual(week_start, datetime.date(2025, 11, 16))
        self.assertEqual(week_start.weekday(), 6)  # Sunday is weekday 6

    def test_calculate_week_dates(self):
        """Test calculating all 7 dates in a week"""
        week_start = datetime.date(2025, 11, 16)  # Sunday
        week_dates = self.service.calculate_week_dates(week_start)
        
        self.assertEqual(len(week_dates), 7)
        self.assertEqual(week_dates[0], datetime.date(2025, 11, 16))  # Sunday
        self.assertEqual(week_dates[6], datetime.date(2025, 11, 22))  # Saturday

    def test_get_current_month_year(self):
        """Test getting current month and year"""
        month, year = self.service.get_current_month_year()
        today = datetime.date.today()
        self.assertEqual(month, today.month)
        self.assertEqual(year, today.year)

    def test_format_month_display_name(self):
        """Test formatting month display name"""
        result = self.service.format_month_display_name(2025, 11)
        self.assertEqual(result, "November 2025")
        
        result = self.service.format_month_display_name(2025, 1)
        self.assertEqual(result, "January 2025")

    def test_format_week_display_name(self):
        """Test formatting week display name"""
        week_start = datetime.date(2025, 11, 16)  # Sunday
        week_end = datetime.date(2025, 11, 22)    # Saturday
        
        result = self.service.format_week_display_name(week_start, week_end)
        self.assertIn("November", result)
        self.assertIn("16", result)
        self.assertIn("22", result)
        self.assertIn("2025", result)


if __name__ == "__main__":
    unittest.main()
