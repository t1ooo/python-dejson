import json
from typing import Any
import enum
from types import UnionType
from typing import Union, get_args, get_origin, Any
from dataclasses import is_dataclass, fields, Field, MISSING

from .errors import (
    ValidationError,
    ValidationErrors,
    ValidationExtraFieldError,
    ValidationFieldRequiredError,
    ValidationTupleLenError,
    ValidationTypeError,
    ValidationTypesError,
)


# TOD0: try to extract type annotation from cls.__init__
# inspect.get_annotations(cls.__init__)
def cls_types(cls: type) -> dict[str, type]:
    types_all = {}

    for typ in reversed(cls.mro()):
        if "__annotations__" in typ.__dict__:
            attrs = typ.__dict__
            types = attrs["__annotations__"]
            types_all.update(types)

    return types_all


def cls_defaults(cls: type) -> dict[str, Any]:
    defaults_all = {}

    for typ in reversed(cls.mro()):
        if "__annotations__" in typ.__dict__:
            attrs = typ.__dict__
            types = attrs["__annotations__"]
            defaults = {k: attrs[k] for k in types.keys() if k in attrs}
            defaults_all.update(defaults)

    return defaults_all


def cls_fields(cls: type) -> dict[str, Field]:
    """Return dataclass fields with with set values default|default_factory"""
    name_field_dict = {}

    if is_dataclass(cls):
        for f in fields(cls):
            if not (f.default is MISSING and f.default_factory is MISSING):
                name_field_dict[f.name] = f

    return name_field_dict


def _type_annotated_class(
    val: Any, typ: Any, keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []

    if type(val) is not dict:
        errors.append(ValidationTypeError(val, dict, keys))
        return None, errors

    types = cls_types(typ)
    defaults = cls_defaults(typ)
    fields = cls_fields(typ)

    for k, v in val.items():
        if k not in types:
            errors.append(
                ValidationExtraFieldError(k, v, list(types.keys()), keys + [k])
            )

    attrs = {}
    for k, t in types.items():
        if k in val:
            v, err = _from_object(val[k], t, keys + [k])
            if err:
                errors.extend(err)
            else:
                attrs[k] = v
        elif k in defaults:
            attrs[k] = defaults[k]
        elif k in fields:
            # ok skip
            continue
        else:
            errors.append(ValidationFieldRequiredError(k, t, keys + [k]))

    if not errors:
        return typ(**attrs), errors

    return None, errors


def _type_type(
    val: Any, typ: Any, keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []
    if isinstance(val, typ):
        return val, errors
    else:
        errors.append(ValidationTypeError(val, typ, keys))
        return None, errors


def _type_enum(
    val: Any, typ: Any, keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []

    for v in typ:
        if val == v.value:
            return v, errors

    errors.append(ValidationTypeError(val, typ, keys))
    return None, errors


def _type_union(
    val: Any, typ_orig: Any, typ_args: tuple[Any, ...], keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []
    for t in typ_args:
        v, err = _from_object(val, t, keys)
        if err:
            pass
            # TODO: ignore?
        else:
            return v, errors

    errors.append(ValidationTypesError(val, typ_args, keys))
    return None, errors


def _type_list(
    val: Any, typ_orig: Any, typ_args: tuple[Any, ...], keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []

    (t,) = typ_args
    res = []
    for k, v in enumerate(val):
        rv, err = _from_object(v, t, keys + [k])
        if err:
            errors.extend(err)
        else:
            res.append(rv)

    return res, errors


def _type_set(
    val: Any, typ_orig: Any, typ_args: tuple[Any, ...], keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    v, err = _type_list(val, typ_orig, typ_args, keys)
    return set(v), err


def _type_tuple(
    val: Any, typ_orig: Any, typ_args: tuple[Any, ...], keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []

    if len(val) != len(typ_args):
        errors.append(ValidationTupleLenError(val, typ_args, keys))

    res = []
    for k, (v, t) in enumerate(zip(val, typ_args)):
        rv, err = _from_object(v, t, keys + [k])
        if err:
            errors.extend(err)
        else:
            res.append(rv)

    return tuple(res), errors


def _type_dict(
    val: Any, typ_orig: Any, typ_args: tuple[Any, ...], keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    errors = []

    if type(val) is not dict:
        errors.append(ValidationTypeError(val, typ_orig, keys))
        return None, errors

    kt, vt = typ_args
    res = {}
    for k, v in val.items():
        rk, err_k = _from_object(k, kt, keys + [k])
        rv, err_v = _from_object(v, vt, keys + [k])
        if err_k or err_v:
            errors.extend(err_k)
            errors.extend(err_v)
        else:
            res[rk] = rv

    return res, errors


# TODO: raise exception when pass not annotated class
# We need to differentiate built-in class from user-defined.
# How to do this without using base class and inheritance?
def _from_object(
    val: Any, typ: Any, keys: list[Any]
) -> tuple[Any, list[ValidationError]]:
    if hasattr(typ, "__dict__") and "__annotations__" in typ.__dict__:
        return _type_annotated_class(val, typ, keys)

    if type(typ) is type:
        return _type_type(val, typ, keys)

    if type(typ) is enum.EnumMeta:
        return _type_enum(val, typ, keys)

    typ_orig = get_origin(typ)
    typ_args = get_args(typ)

    if typ_orig in (UnionType, Union):
        return _type_union(val, typ_orig, typ_args, keys)

    if typ_orig in [tuple, set, list]:
        if type(val) in [tuple, set, list]:
            if typ_orig is list:
                return _type_list(val, typ_orig, typ_args, keys)

            if typ_orig is set:
                return _type_set(val, typ_orig, typ_args, keys)

            if typ_orig is tuple:
                return _type_tuple(val, typ_orig, typ_args, keys)

        return None, [ValidationTypesError(val, [tuple, set, list], keys)]

    if typ_orig is dict:
        return _type_dict(val, typ_orig, typ_args, keys)

    raise Exception(f"unsupported type: {typ}, val: {val}")


def from_object(val: Any, typ: Any) -> Any:
    res, err = _from_object(val, typ, [])
    if err:
        raise ValidationErrors(typ, err)
    return res


def from_json(s: str | bytes | bytearray, typ: Any) -> Any:
    d = json.loads(s)
    return from_object(d, typ)
