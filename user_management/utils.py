from django.contrib.gis.geoip2 import GeoIP2
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get("HTTP_USER_AGENT", "")[:500]  # Limit length


def get_location_from_ip(ip_address):
    """Get location information from IP address"""
    try:
        g = GeoIP2()
        location = g.city(ip_address)
        return {
            "city": location.get("city", ""),
            "country": location.get("country_name", ""),
            "country_code": location.get("country_code", ""),
        }
    except:
        return {"city": "", "country": "", "country_code": ""}


def parse_user_agent(user_agent_string):
    """Parse user agent string to extract browser and OS info"""
    # Simple regex patterns for common browsers and OS
    browsers = {
        "Chrome": r"Chrome/[\d.]+",
        "Firefox": r"Firefox/[\d.]+",
        "Safari": r"Safari/[\d.]+",
        "Edge": r"Edge/[\d.]+",
    }

    operating_systems = {
        "Windows": r"Windows NT [\d.]+",
        "macOS": r"Mac OS X [\d._]+",
        "Linux": r"Linux",
        "Android": r"Android [\d.]+",
        "iOS": r"OS [\d_]+",
    }

    browser = "Unknown"
    os = "Unknown"

    for name, pattern in browsers.items():
        if re.search(pattern, user_agent_string, re.I):
            browser = name
            break

    for name, pattern in operating_systems.items():
        if re.search(pattern, user_agent_string, re.I):
            os = name
            break

    return {"browser": browser, "os": os}


def validate_email_format(email):
    """Validate email format"""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def generate_username_from_email(email):
    """Generate a unique username from email"""
    from django.contrib.auth import get_user_model

    User = get_user_model()

    base_username = email.split("@")[0]
    username = base_username
    counter = 1

    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username


def sanitize_redirect_url(url, allowed_domains=None):
    """Sanitize redirect URL to prevent open redirects"""
    if not url:
        return None

    from urllib.parse import urlparse

    parsed = urlparse(url)

    # Only allow http/https schemes
    if parsed.scheme not in ["http", "https"]:
        return None

    # If allowed domains specified, check against them
    if allowed_domains:
        if parsed.netloc not in allowed_domains:
            return None

    return url
