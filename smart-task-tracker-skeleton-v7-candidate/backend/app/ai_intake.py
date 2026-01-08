"""
FAKE AI Intake Adapter for Smart Task Tracker.

This is a deterministic fake implementation that extracts title and priority
from user input text. In production, this would call an LLM API.

Rules:
- Title: Extract first sentence or first 50 chars, cleaned up
- Priority: Based on keyword detection (urgent/asap = High, later/low = Low, default = Med)
"""
import re
from typing import Tuple

# Keywords for priority detection
HIGH_PRIORITY_KEYWORDS = [
    "urgent", "asap", "immediately", "critical", "emergency", 
    "high priority", "important", "deadline", "today", "now",
    "must", "crucial", "vital"
]

LOW_PRIORITY_KEYWORDS = [
    "later", "low priority", "when possible", "eventually", 
    "someday", "nice to have", "optional", "whenever", "no rush"
]


def extract_title(text: str) -> str:
    """
    Extract a task title from the input text.
    Takes the first sentence or first 50 characters.
    """
    text = text.strip()
    
    # Try to get first sentence
    sentence_match = re.match(r'^([^.!?]+[.!?]?)', text)
    if sentence_match:
        title = sentence_match.group(1).strip()
    else:
        title = text
    
    # Clean up the title
    title = re.sub(r'\s+', ' ', title)  # Normalize whitespace
    
    # Truncate if too long
    if len(title) > 100:
        title = title[:97] + "..."
    
    # Remove leading action words for cleaner titles
    action_prefixes = [
        r"^(I need to|We need to|Need to|Please|Can you|Could you|Should|Must|Have to) ",
        r"^(Remember to|Don't forget to|Make sure to) ",
    ]
    for pattern in action_prefixes:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)
    
    # Capitalize first letter
    if title:
        title = title[0].upper() + title[1:]
    
    return title or "New Task"


def detect_priority(text: str) -> str:
    """
    Detect priority based on keywords in the text.
    Returns: "High", "Med", or "Low"
    """
    text_lower = text.lower()
    
    # Check for high priority keywords
    for keyword in HIGH_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            return "High"
    
    # Check for low priority keywords
    for keyword in LOW_PRIORITY_KEYWORDS:
        if keyword in text_lower:
            return "Low"
    
    # Default to medium
    return "Med"


def process_intake(input_text: str) -> Tuple[str, str]:
    """
    Process user input and return suggested title and priority.
    
    Args:
        input_text: Raw text from user (e.g., pasted paragraph)
    
    Returns:
        Tuple of (title, priority)
    """
    title = extract_title(input_text)
    priority = detect_priority(input_text)
    
    return title, priority

