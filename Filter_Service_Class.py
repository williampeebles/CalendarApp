import datetime


class FilterService:
    """
    Service class for filtering calendar events based on various criteria.
    
    This class handles all filter logic and data processing for events,
    separating concerns from the UI (FilterDialog) and core calendar logic.
    """
    
    def __init__(self, database_date_format="%d-%m-%Y"):
        """
        Initialize the FilterService.
        
        Args:
            database_date_format (str): Date format used for event date strings
        """
        self.DATABASE_DATE_FORMAT = database_date_format
    
    def filter_events(self, events, filter_criteria):
        """
        Filter a list of events based on multiple criteria.

        Args:
            events (list): List of Event objects to filter
            filter_criteria (dict): Dictionary containing filter options:
                - search_text (str): Text to search in title/description
                - from_date (datetime.date): Start of date range
                - to_date (datetime.date): End of date range
                - show_all_day (bool): Include all-day events
                - show_timed (bool): Include timed events
                - show_recurring (bool): Include recurring events

        Returns:
            list: Filtered list of Event objects
        """
        if not filter_criteria:
            return events

        filtered = []
        search_text = filter_criteria.get('search_text', '').lower()
        from_date = filter_criteria.get('from_date')
        to_date = filter_criteria.get('to_date')
        show_all_day = filter_criteria.get('show_all_day', True)
        show_timed = filter_criteria.get('show_timed', True)
        show_recurring = filter_criteria.get('show_recurring', True)

        for event in events:
            # Apply all filters
            if not self._matches_text_filter(event, search_text):
                continue
            
            if not self._matches_date_filter(event, from_date, to_date):
                continue
            
            if not self._matches_type_filter(event, show_all_day, show_timed, show_recurring):
                continue

            filtered.append(event)

        return filtered
    
    def _matches_text_filter(self, event, search_text):
        """
        Check if event matches text search criteria.
        
        Args:
            event: Event object to check
            search_text (str): Text to search for in title/description
            
        Returns:
            bool: True if event matches or no search text provided
        """
        if not search_text:
            return True
        
        title_match = search_text in event.title.lower()
        desc_match = search_text in event.description.lower()
        return title_match or desc_match
    
    def _matches_date_filter(self, event, from_date, to_date):
        """
        Check if event falls within the specified date range.
        
        Args:
            event: Event object to check
            from_date (datetime.date): Start of date range
            to_date (datetime.date): End of date range
            
        Returns:
            bool: True if event is within range or no dates provided
        """
        if not from_date or not to_date:
            return True
        
        try:
            event_date = datetime.datetime.strptime(event.date, self.DATABASE_DATE_FORMAT).date()
            return from_date <= event_date <= to_date
        except (ValueError, AttributeError):
            return False
    
    def _matches_type_filter(self, event, show_all_day, show_timed, show_recurring):
        """
        Check if event matches the event type filters.
        
        Args:
            event: Event object to check
            show_all_day (bool): Whether to include all-day events
            show_timed (bool): Whether to include timed events
            show_recurring (bool): Whether to include recurring events
            
        Returns:
            bool: True if event matches type criteria
        """
        # Check all-day filter
        if event.is_all_day and not show_all_day:
            return False
        
        # Check timed event filter
        if not event.is_all_day and not show_timed:
            return False
        
        # Check recurring filter
        if event.is_recurring and not show_recurring:
            return False
        
        return True
    
    def get_filter_summary(self, filter_criteria):
        """
        Generate a human-readable summary of applied filters.
        
        Args:
            filter_criteria (dict): Dictionary containing filter options
            
        Returns:
            str: Description of active filters
        """
        if not filter_criteria:
            return "No filters applied"
        
        summary_parts = []
        
        # Text search
        search_text = filter_criteria.get('search_text', '')
        if search_text:
            summary_parts.append(f"Text: '{search_text}'")
        
        # Date range
        from_date = filter_criteria.get('from_date')
        to_date = filter_criteria.get('to_date')
        if from_date and to_date:
            summary_parts.append(f"Date: {from_date.strftime('%d-%m-%Y')} to {to_date.strftime('%d-%m-%Y')}")
        
        # Event types
        show_all_day = filter_criteria.get('show_all_day', True)
        show_timed = filter_criteria.get('show_timed', True)
        show_recurring = filter_criteria.get('show_recurring', True)
        
        type_filters = []
        if not show_all_day:
            type_filters.append("All-Day")
        if not show_timed:
            type_filters.append("Timed")
        if not show_recurring:
            type_filters.append("Recurring")
        
        if type_filters:
            summary_parts.append(f"Excluding: {', '.join(type_filters)}")
        
        return " | ".join(summary_parts) if summary_parts else "All events (no restrictions)"
    
    def validate_filter_criteria(self, filter_criteria):
        """
        Validate filter criteria and return any errors.
        
        Args:
            filter_criteria (dict): Dictionary containing filter options
            
        Returns:
            list: List of error messages (empty if valid)
        """
        errors = []
        
        if not filter_criteria:
            return errors
        
        # Validate date range
        from_date = filter_criteria.get('from_date')
        to_date = filter_criteria.get('to_date')
        
        if from_date and to_date:
            if from_date > to_date:
                errors.append("'From' date must be before or equal to 'To' date")
        
        # Validate at least one event type is selected
        show_all_day = filter_criteria.get('show_all_day', True)
        show_timed = filter_criteria.get('show_timed', True)
        show_recurring = filter_criteria.get('show_recurring', True)
        
        if not (show_all_day or show_timed or show_recurring):
            errors.append("At least one event type must be selected")
        
        return errors
