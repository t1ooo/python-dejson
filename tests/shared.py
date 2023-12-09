from typing import Any
from python_dejson.errors import ValidationErrors
from python_dejson.dejson import *


def err_to_dict(err: ValidationErrors) -> dict[str, Any]:
    return dict(
        class_type=err.class_type,
        errors=[{**vars(e), **{"cls": e.__class__}} for e in err.errors],
    )


def from_object_val(val: Any, typ: Any) -> Any:
    try:
        return from_object(val, typ)
    except ValidationErrors:
        return None


def from_object_err(val: Any, typ: Any) -> Any:
    try:
        from_object(val, typ)
        return None
    except ValidationErrors as e:
        return e
