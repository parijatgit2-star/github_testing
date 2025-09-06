from typing import Any, List, Type


def _instantiate_model(model: Type[Any], data: Any):
    """Instantiates a Pydantic model, handling v1/v2 compatibility.

    This helper function attempts to validate and create a Pydantic model
    instance using the recommended methods for Pydantic v2 (`model_validate`)
    and v1 (`parse_obj`) before falling back to the standard constructor.

    Args:
        model: The Pydantic model class to instantiate.
        data: The raw data (e.g., a dictionary) to populate the model with.

    Returns:
        An instance of the Pydantic model, or None if the input data is None.
    """
    if data is None:
        return None
    try:
        if hasattr(model, 'model_validate'):
            return model.model_validate(data)
        if hasattr(model, 'parse_obj'):
            return model.parse_obj(data)
        return model(**(data or {}))
    except Exception:
        # Last-resort fallback to constructor; let FastAPI surface validation errors if any.
        return model(**(data or {}))


def validate_list(model: Type[Any], rows: List[Any]) -> List[Any]:
    """Validates a list of raw data objects into a list of Pydantic models.

    Args:
        model: The Pydantic model class to instantiate for each item.
        rows: A list of raw data objects (e.g., dicts from a database).

    Returns:
        A list of Pydantic model instances.
    """
    return [_instantiate_model(model, r) for r in (rows or [])]


def validate_single(model: Type[Any], row: Any) -> Any:
    """Validates a single raw data object into a Pydantic model instance.

    Args:
        model: The Pydantic model class to instantiate.
        row: A single raw data object (e.g., a dict from a database).

    Returns:
        A Pydantic model instance.
    """
    return _instantiate_model(model, row)
