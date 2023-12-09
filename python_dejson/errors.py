from typing import Any


class ValidationError:
    keys: list[Any]


class ValidationErrors(ValueError):
    def __init__(self, class_type: type, errors: list[ValidationError]):
        self.class_type = class_type
        self.errors = errors

    def __len__(self):
        return len(self.errors)

    def __str__(self):
        lines: list[str] = []

        lines.append(f"{len(self)} validation error(s) for {self.class_type}")
        for err in self.errors:
            k = ".".join(map(str, err.keys))
            lines.append(k)
            lines.append("  " + str(err))

        return "\n".join(lines)


class ValidationExtraFieldError(ValidationError):
    def __init__(
        self,
        name: str,
        value: Any,
        expected_names: list[str],
        keys: list[Any],
    ):
        self.name = name
        self.type = type(value)
        self.value = value
        self.expected_names = expected_names
        self.keys = keys

    def __str__(self):
        return f"expected: fields={self.expected_names}; got: field={self.name} val={self.value} type={self.type}"


class ValidationAnnotationError(ValidationError):
    def __init__(
        self,
        val: Any,
        type: type,
        keys: list[Any],
    ):
        self.val = val
        self.type = type
        self.keys = keys

    def __str__(self):
        return f"expected annotated class: value={self.val} type={self.type}"


class ValidationFieldRequiredError(ValidationError):
    def __init__(
        self,
        name: str,
        type: type,
        keys: list[Any],
    ):
        self.name = name
        self.type = type
        self.keys = keys

    def __str__(self):
        return f"expected: field={self.name} type={self.type}; got: nothing"


class ValidationTypeError(ValidationError):
    def __init__(
        self,
        value: Any,
        expected_type: Any,
        keys: list[Any],
    ):
        self.value = value
        self.type = type(value)
        self.expected_type = expected_type
        self.keys = keys

    def __str__(self):
        return f"expected: type={self.expected_type}; got: value={self.value}, type={self.type}"


class ValidationTypesError(ValidationError):
    def __init__(
        self,
        value: Any,
        expected_types: tuple[Any, ...],
        keys: list[Any],
    ):
        self.value = value
        self.type = type(value)
        self.expected_types = expected_types
        self.keys = keys

    def __str__(self):
        return f"expected: types={self.expected_types}; got: value={self.value}, type={self.type}"


class ValidationTupleLenError(ValidationError):
    def __init__(
        self,
        value: Any,
        expected_types: tuple[Any, ...],
        keys: list[Any],
    ):
        self.value = value
        self.len = len(value)
        self.expected_len = len(expected_types)
        self.keys = keys

    def __str__(self):
        return f"expected: tuple_len={self.expected_len}; got: tuple_len={self.len}, tuple={self.value}"
