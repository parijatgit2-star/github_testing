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
    if not text:
        return None
    t = text.lower()
    for kw, dept in KEYWORD_MAP.items():
        if kw in t:
            return dept
    return None


def map_department_name_to_id(departments: Dict[str, str], name: str) -> Optional[str]:
    """Given a mapping of department rows (id->name) or name->id, return the id for the given name.
    departments may be a dict where keys are ids and values are names, or vice-versa.
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
