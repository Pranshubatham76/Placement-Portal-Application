"""Helper utility functions"""

from datetime import datetime
from app.utils.constants import (
    DISPLAY_DATE_FORMAT,
    DISPLAY_DATETIME_FORMAT,
    DATE_FORMAT,
    DATETIME_FORMAT
)


def format_date(date_obj, format_str=None):
    """
    Format date object to string
    
    Args:
        date_obj (datetime): Date object
        format_str (str): Format string (default: display format)
    
    Returns:
        str: Formatted date string
    """
    if not date_obj:
        return ""
    
    if format_str is None:
        format_str = DISPLAY_DATE_FORMAT
    
    return date_obj.strftime(format_str)


def format_datetime(datetime_obj, format_str=None):
    """
    Format datetime object to string
    
    Args:
        datetime_obj (datetime): Datetime object
        format_str (str): Format string (default: display format)
    
    Returns:
        str: Formatted datetime string
    """
    if not datetime_obj:
        return ""
    
    if format_str is None:
        format_str = DISPLAY_DATETIME_FORMAT
    
    return datetime_obj.strftime(format_str)


def parse_date(date_str, format_str=None):
    """
    Parse date string to datetime object
    
    Args:
        date_str (str): Date string
        format_str (str): Format string (default: standard format)
    
    Returns:
        datetime: Datetime object or None if invalid
    """
    if not date_str:
        return None
    
    if format_str is None:
        format_str = DATE_FORMAT
    
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def time_ago(datetime_obj):
    """
    Get human-readable time ago string
    
    Args:
        datetime_obj (datetime): Datetime object
    
    Returns:
        str: Time ago string (e.g., "2 hours ago")
    """
    if not datetime_obj:
        return ""
    
    now = datetime.utcnow()
    diff = now - datetime_obj
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 31536000:  # 365 days
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def get_days_until(target_date):
    """
    Get number of days until target date
    
    Args:
        target_date (datetime): Target date
    
    Returns:
        int: Number of days (negative if past)
    """
    if not target_date:
        return 0
    
    now = datetime.utcnow()
    diff = target_date - now
    
    return diff.days


def truncate_text(text, max_length=100, suffix='...'):
    """
    Truncate text to maximum length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add if truncated
    
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_initials(name):
    """
    Get initials from name
    
    Args:
        name (str): Full name
    
    Returns:
        str: Initials (e.g., "John Doe" -> "JD")
    """
    if not name:
        return ""
    
    parts = name.strip().split()
    if len(parts) == 1:
        return parts[0][0].upper()
    
    return ''.join([part[0].upper() for part in parts[:2]])


def format_currency(amount):
    """
    Format amount as currency (INR)
    
    Args:
        amount (float): Amount
    
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "N/A"
    
    # Indian currency format
    if amount >= 10000000:  # 1 Crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 Lakh
        return f"₹{amount/100000:.2f} L"
    elif amount >= 1000:  # 1 Thousand
        return f"₹{amount/1000:.2f} K"
    else:
        return f"₹{amount:.2f}"


def format_number(number):
    """
    Format number with thousands separator
    
    Args:
        number (int/float): Number
    
    Returns:
        str: Formatted number
    """
    if number is None:
        return "0"
    
    return f"{number:,}"


def generate_unique_filename(original_filename, prefix=''):
    """
    Generate unique filename with timestamp
    
    Args:
        original_filename (str): Original filename
        prefix (str): Prefix to add
    
    Returns:
        str: Unique filename
    """
    import os
    import uuid
    
    # Get file extension
    _, ext = os.path.splitext(original_filename)
    
    # Generate unique ID
    unique_id = uuid.uuid4().hex[:10]
    
    # Create timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Combine
    if prefix:
        return f"{prefix}_{timestamp}_{unique_id}{ext}"
    else:
        return f"{timestamp}_{unique_id}{ext}"


def sanitize_filename(filename):
    """
    Sanitize filename to remove dangerous characters
    
    Args:
        filename (str): Filename
    
    Returns:
        str: Sanitized filename
    """
    import re
    
    # Remove path separators and dangerous characters
    filename = filename.replace('/', '_').replace('\\', '_')
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    return filename.strip()


def paginate_query(query, page=1, per_page=20):
    """
    Paginate SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page (int): Page number (1-indexed)
        per_page (int): Items per page
    
    Returns:
        dict: Pagination data with items, total, pages, etc.
    """
    from app.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
    
    # Validate page number
    if page < 1:
        page = 1
    
    # Validate per_page
    if per_page < 1:
        per_page = DEFAULT_PAGE_SIZE
    elif per_page > MAX_PAGE_SIZE:
        per_page = MAX_PAGE_SIZE
    
    # Get total count
    total = query.count()
    
    # Calculate total pages
    if total == 0:
        total_pages = 1
    else:
        total_pages = (total + per_page - 1) // per_page
    
    # Ensure page doesn't exceed total pages
    if page > total_pages:
        page = total_pages
    
    # Get items
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }
