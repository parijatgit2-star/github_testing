from typing import Any, List, Type


def _instantiate_model(model: Type[Any], data: Any):
    """Instantiate a Pydantic model from raw data with compatibility helpers.
    Tries model.model_validate (Pydantic v2), then model.parse_obj (v1), then model(**data).
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
    return [_instantiate_model(model, r) for r in (rows or [])]


def validate_single(model: Type[Any], row: Any) -> Any:
    return _instantiate_model(model, row)
