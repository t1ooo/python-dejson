from typing import Dict, List, Set, Tuple, Union
from python_dejson.errors import (
    ValidationTupleLenError,
    ValidationTypeError,
    ValidationTypesError,
)
from .shared import err_to_dict, from_object_err, from_object_val


def test_simple():
    assert from_object_val(1, int) == 1
    assert from_object_val("1", str) == "1"
    assert from_object_val(2.3, float) == 2.3


def test_tuple():
    assert from_object_val((1, 2), tuple[int, int]) == (1, 2)
    assert from_object_val([1, 2], tuple[int, int]) == (1, 2)
    assert from_object_val([1, 2, 3], tuple[int, int]) == None
    assert from_object_val(["1", 2], tuple[int, int]) == None
    assert from_object_val({1: 2}, tuple[int, int]) == None

    assert from_object_val((1, 2), Tuple[int, int]) == (1, 2)
    assert from_object_val([1, 2], Tuple[int, int]) == (1, 2)
    assert from_object_val([1, 2, 3], Tuple[int, int]) == None
    assert from_object_val(["1", 2], Tuple[int, int]) == None
    assert from_object_val({1: 2}, Tuple[int, int]) == None

    err = from_object_err([1, 2, 3], tuple[int, int])
    assert err_to_dict(err) == {
        "class_type": tuple[int, int],
        "errors": [
            {
                "cls": ValidationTupleLenError,
                "value": [1, 2, 3],
                "len": 3,
                "expected_len": 2,
                "keys": [],
            }
        ],
    }

    err = from_object_err(["1", 2], tuple[int, int])
    assert err_to_dict(err) == {
        "class_type": tuple[int, int],
        "errors": [
            {
                "cls": ValidationTypeError,
                "value": "1",
                "type": str,
                "expected_type": int,
                "keys": [0],
            }
        ],
    }


def test_dict():
    assert from_object_val({1: 2}, dict[int, int]) == {1: 2}
    assert from_object_val({"1": 2}, dict[int, int]) == None
    assert from_object_val({1: "2"}, dict[int, int]) == None

    assert from_object_val({1: 2}, Dict[int, int]) == {1: 2}
    assert from_object_val({"1": 2}, Dict[int, int]) == None
    assert from_object_val({1: "2"}, Dict[int, int]) == None

    err = from_object_err({"1": 2}, dict[int, int])
    assert err_to_dict(err) == {
        "class_type": dict[int, int],
        "errors": [
            {
                "cls": ValidationTypeError,
                "value": "1",
                "type": str,
                "expected_type": int,
                "keys": ["1"],
            }
        ],
    }

    err = from_object_err({1: "2"}, dict[int, int])
    assert err_to_dict(err) == {
        "class_type": dict[int, int],
        "errors": [
            {
                "cls": ValidationTypeError,
                "value": "2",
                "type": str,
                "expected_type": int,
                "keys": [1],
            }
        ],
    }


def test_list():
    assert from_object_val([1, 2], list[int]) == [1, 2]
    assert from_object_val([1, 2], list[int]) == [1, 2]
    assert from_object_val([1, 2, 3], list[int]) == [1, 2, 3]
    assert from_object_val(["1", 2], list[int]) == None
    assert from_object_val({1: 2}, list[int]) == None

    assert from_object_val([1, 2], List[int]) == [1, 2]
    assert from_object_val([1, 2], List[int]) == [1, 2]
    assert from_object_val([1, 2, 3], List[int]) == [1, 2, 3]
    assert from_object_val(["1", 2], List[int]) == None
    assert from_object_val({1: 2}, List[int]) == None

    err = from_object_err(["1", 2], list[int])
    assert err_to_dict(err) == {
        "class_type": list[int],
        "errors": [
            {
                "cls": ValidationTypeError,
                "value": "1",
                "type": str,
                "expected_type": int,
                "keys": [0],
            }
        ],
    }


def test_set():
    assert from_object_val({1, 2}, set[int]) == {1, 2}
    assert from_object_val([1, 2], set[int]) == {1, 2}
    assert from_object_val({1, 2}, set[int]) == {1, 2}
    assert from_object_val({1, 2, 3}, set[int]) == {1, 2, 3}
    assert from_object_val({"1", 2}, set[int]) == None
    assert from_object_val({1: 2}, set[int]) == None

    assert from_object_val({1, 2}, Set[int]) == {1, 2}
    assert from_object_val([1, 2], Set[int]) == {1, 2}
    assert from_object_val({1, 2}, Set[int]) == {1, 2}
    assert from_object_val({1, 2, 3}, Set[int]) == {1, 2, 3}
    assert from_object_val({"1", 2}, Set[int]) == None
    assert from_object_val({1: 2}, Set[int]) == None

    err = from_object_err(["1", 2], set[int])
    assert err_to_dict(err) == {
        "class_type": set[int],
        "errors": [
            {
                "cls": ValidationTypeError,
                "value": "1",
                "type": str,
                "expected_type": int,
                "keys": [0],
            }
        ],
    }


def test_union():
    assert from_object_val(1, int | str) == 1
    assert from_object_val("1", int | str) == "1"
    assert from_object_val([], int | str) == None

    assert from_object_val(1, Union[int, str]) == 1
    assert from_object_val("1", Union[int, str]) == "1"
    assert from_object_val([], Union[int, str]) == None

    err = from_object_err([], int | str)
    assert err_to_dict(err) == {
        "class_type": int | str,
        "errors": [
            {
                "cls": ValidationTypesError,
                "value": [],
                "type": list,
                "expected_types": (int, str),
                "keys": [],
            }
        ],
    }


def test_complex_type():
    assert from_object_val([[{1: 2}], [{3: 4}]], list[list[dict[int, int]]]) == [
        [{1: 2}],
        [{3: 4}],
    ]
