from dataclasses import dataclass, field
import enum
from python_dejson.errors import ValidationErrors
from python_dejson.dejson import from_json, from_object



class A(enum.Enum):
    a = 1
    b = 2
    c = 2


@dataclass(frozen=True)
class D:
    x: A


@dataclass(frozen=True)
class Base:
    a: str


# define some complex class with type annotations
@dataclass(frozen=True)
class ComplexClass(Base):
    b: tuple[int, str]
    c: dict[str, int]
    d: list[int]
    e: A
    f: D
    g: int | str
    h: set[int] = field(default_factory=lambda: {9, 9, 9, 9})


t = ComplexClass(
    a="1",
    b=(1, "s"),
    c={"s": 1},
    d=[1, 2, 3],
    e=A.a,
    f=D(x=A.b),
    g=1,
    h=set([1, 2, 3]),
)

# create an instance of the ComplexClass from a dict
data = {
    "a": "1",
    "b": [1, "s"],
    "c": {"s": 1},
    "d": [1, 2, 3],
    "e": 1,
    "f": {"x": 2},
    "g": 1,
    "h": [9],
}
print(from_object(data, ComplexClass), end="\n\n")
# print:
# ComplexClass(a='1', b=(1, 's'), c={'s': 1}, d=[1, 2, 3], e=<A.a: 1>, f=D(x=<A.b: 2>), g=1, h={9})


# create an instance of the ComplexClass from a json
data = '{"a": "1", "b": [1, "s"], "c": {"s": 1}, "d": [1, 2, 3], "e": 1, "f": {"x": 2}, "g": 1, "h": [9]}'
print(from_json(data, ComplexClass), end="\n\n")
# print:
# ComplexClass(a='1', b=(1, 's'), c={'s': 1}, d=[1, 2, 3], e=<A.a: 1>, f=D(x=<A.b: 2>), g=1, h={9})


# create an instance of the ComplexClass from a dict and print an error message
try:
    data = {
        "a": 1,
        "b": ["1", "s", 3],
        "c": {"s": 1},
        "d": [1, 2, 3],
        "e": 1,
        "f": {"x": 4},
        "g": 8,
        "h": ["9"],
    }
    from_object(data, ComplexClass)
except ValidationErrors as e:
    print("-" * 50)
    print(e, end="\n\n")
# print:
# --------------------------------------------------
# 5 validation error(s) for <class '__main__.ComplexClass'>
# a
#   expected: type=<class 'str'>; got: value=1, type=<class 'int'>
# b
#   expected: tuple_len=2; got: tuple_len=3, tuple=['1', 's', 3]
# b.0
#   expected: type=<class 'int'>; got: value=1, type=<class 'str'>
# f.x
#   expected: type=<enum 'A'>; got: value=4, type=<class 'int'>
# h.0
#   expected: type=<class 'int'>; got: value=9, type=<class 'str'>


# create an instance of the ComplexClass from a json and print an error message
try:
    from_json("{}", ComplexClass)
except ValidationErrors as e:
    print("-" * 50)
    print(e, end="\n\n")
# print:
# --------------------------------------------------
# 7 validation error(s) for <class '__main__.ComplexClass'>
# a
#   expected: field=a type=<class 'str'>; got: nothing
# b
#   expected: field=b type=tuple[int, str]; got: nothing
# c
#   expected: field=c type=dict[str, int]; got: nothing
# d
#   expected: field=d type=list[int]; got: nothing
# e
#   expected: field=e type=<enum 'A'>; got: nothing
# f
#   expected: field=f type=<class '__main__.D'>; got: nothing
# g
#   expected: field=g type=int | str; got: nothing
