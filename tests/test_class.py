from dataclasses import dataclass, field
import enum
from typing import Any
from python_dejson.errors import (
    ValidationErrors,
    ValidationExtraFieldError,
    ValidationFieldRequiredError,
    ValidationTypeError,
    ValidationTypesError,
)
from python_dejson.dejson import cls_types, from_object
from .shared import from_object_err


def test_complex():
    class A(enum.Enum):
        a = 1
        b = 2
        c = 2

    class B:
        x: A

        def __init__(self, **data: Any):
            for k in cls_types(type(self)).keys():
                setattr(self, k, data[k])

    class C:
        z: int

        def __init__(self, **data: Any):
            for k in cls_types(type(self)).keys():
                setattr(self, k, data[k])

    class Complex(C):
        a: str
        b: tuple[int, str]
        c: dict[str, int]
        d: list[int]
        e: A
        f: B
        g: int | str
        h: set[int]

        def __init__(self, **data: Any):
            for k in cls_types(type(self)).keys():
                setattr(self, k, data[k])

    t = Complex(
        a="1",
        b=(1, "s"),
        c={"s": 1},
        d=[1, 2, 3],
        e=A.a,
        f=B(x=A.b),
        g=1,
        h=set([1, 2, 3]),
        z=1,
    )
    d = {
        "z": 1,
        "a": "1",
        "b": [1, "s"],
        "c": {"s": 1},
        "d": [1, 2, 3],
        "e": 1,
        "f": {"x": 2},
        "g": 1,
        "h": [1, 2, 3],
    }
    t2 = from_object(d, Complex)
    assert t.a == t2.a
    assert t.b == t2.b
    assert t.c == t2.c
    assert t.d == t2.d
    assert t.e == t2.e
    assert t.f.x == t2.f.x
    assert t.g == t2.g
    assert t.h == t2.h
    assert t.z == t2.z


def test_simple():
    class Simple:
        a: int
        b: str
        c: float

        def __init__(self, a: int, b: str, c: float):
            self.a = a
            self.b = b
            self.c = c

    t = Simple(1, "1", 1.1)
    t2 = from_object({"a": 1, "b": "1", "c": 1.1}, Simple)
    assert t.a == t2.a
    assert t.b == t2.b
    assert t.c == t2.c


def test_missing_field():
    class Simple:
        a: int
        b: str
        c: float

        def __init__(self, a: int, b: str, c: float):
            self.a = a
            self.b = b
            self.c = c

    d = {"a": 1, "b": "1", "c": 1.1}

    for k in d.keys():
        d_cloned = d.copy()
        del d_cloned[k]

        err = from_object_err(d_cloned, Simple)

        assert type(err) is ValidationErrors
        assert len(err) == 1
        assert len(err) == len(err.errors)

        e = err.errors[0]
        assert type(e) is ValidationFieldRequiredError
        assert e.name == k
        assert e.keys == [k]


def test_defaults():
    class Base:
        a: int = 1

    class Simple(Base):
        b: str = "1"
        c: float = 1.1

        def __init__(self, a: int, b: str, c: float):
            self.a = a
            self.b = b
            self.c = c

    # should fill from defaults
    d = {}
    t2 = from_object(d, Simple)
    assert t2.a == 1
    assert t2.b == "1"
    assert t2.c == 1.1

    # should rewrite defaults
    d = {"a": 99, "b": "99", "c": 99.99}
    t2 = from_object(d, Simple)
    assert t2.a == 99
    assert t2.b == "99"
    assert t2.c == 99.99


def test_dataclass_defaults_fields():
    @dataclass
    class Base:
        a: int = field(default=1)

    @dataclass
    class Simple(Base):
        b: str = field(default="1")
        c: float = field(default=1.1)

        def __init__(self, a: int, b: str, c: float):
            self.a = a
            self.b = b
            self.c = c

    # should fill from defaults
    d = {"b": "1"}
    t2 = from_object(d, Simple)
    assert t2.a == 1
    assert t2.b == "1"
    assert t2.c == 1.1

    # should rewrite defaults
    d = {"a": 99, "b": "99", "c": 99.99}
    t2 = from_object(d, Simple)
    assert t2.a == 99
    assert t2.b == "99"
    assert t2.c == 99.99


def test_wrong_type():
    class Simple:
        a: int
        b: str
        c: float

        def __init__(self, a: int, b: str, c: float):
            self.a = a
            self.b = b
            self.c = c

    data = [
        ("a", {"a": [1], "b": "1", "c": 1.1}),
        ("b", {"a": 1, "b": {"1"}, "c": 1.1}),
        ("c", {"a": 1, "b": "1", "c": {"a": 1.1}}),
    ]

    for k, d in data:
        err = from_object_err(d, Simple)

        assert type(err) is ValidationErrors
        assert len(err) == 1
        assert len(err) == len(err.errors)
        e = err.errors[0]

        assert type(e) in [ValidationTypeError, ValidationTypesError]
        assert e.type is type(d[k])
        assert e.value == d[k]
        assert e.keys == [k]


def test_extra_fields():
    class Simple:
        a: int
        b: str
        c: float

        def __init__(self, a: int, b: str, c: float):
            self.a = a
            self.b = b
            self.c = c

    k = "extra"
    v = 1
    d = {"a": 1, "b": "1", "c": 1.1, k: v}

    err = from_object_err(d, Simple)
    assert type(err) is ValidationErrors
    assert len(err) == 1
    assert len(err) == len(err.errors)

    e = err.errors[0]
    assert type(e) is ValidationExtraFieldError
    assert e.name == k
    assert e.type is type(v)
    assert e.keys == [k]
