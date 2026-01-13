import re
from urllib.parse import urlparse

def normalize_url(url: str) -> str:
    """
    Normalizes a URL to ensure it has a scheme and is stripped of trailing slashes.
    """
    if not url:
        return ""
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    parsed = urlparse(url)
    
    # Reconstruct url without fragment/query if needed, or keep them.
    # For a business homepage, we usually want just scheme + netloc + path
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    if normalized.endswith('/'):
        normalized = normalized[:-1]
        
    return normalized

def validate_email(email: str) -> bool:
    """
    Basic email validation using regex.
    """
    if not email:
        return False
    # Simple regex for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))
