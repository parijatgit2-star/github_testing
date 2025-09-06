from typing import Optional, Dict


# Simple keyword-based routing engine
KEYWORD_MAP = {
    'pothole': 'Public Works',
    'sinkhole': 'Public Works',
    'streetlight': 'Public Works',
    'garbage': 'Sanitation',
    'trash': 'Sanitation',
    'overflow': 'Sanitation',
}


def detect_department_from_text(text: str) -> Optional[str]:
    """Detects a likely department name from text based on keywords.

    Args:
        text: The input string to analyze (e.g., an issue description).

    Returns:
        The name of the matched department, or None if no keyword is found.
    """
    if not text:
        return None
    t = text.lower()
    for kw, dept in KEYWORD_MAP.items():
        if kw in t:
            return dept
    return None


def map_department_name_to_id(departments: Dict[str, str], name: str) -> Optional[str]:
    """Finds a department ID from a name, supporting forward and reverse mappings.

    This utility function is designed to work with two possible dictionary
    formats for the `departments` mapping:
    1.  `{department_id: department_name}`
    2.  `{department_name: department_id}`

    It checks for the name in both keys and values to find the corresponding ID.

    Args:
        departments: A dictionary mapping department IDs to names, or names to IDs.
        name: The name of the department to find the ID for.

    Returns:
        The matching department ID as a string, or None if not found.
    """
    if not name:
        return None
    # first try name->id mapping
    if name in departments:
        return departments.get(name)
    # then try id->name mapping
    for k, v in departments.items():
        if isinstance(v, str) and v.lower() == name.lower():
            return k
    return None
