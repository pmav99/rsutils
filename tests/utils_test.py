import pathlib

import pendulum
import pytest

from rsutils.utils import to_python, to_boolean, NULL_VALUES


@pytest.mark.parametrize(
    "value, expected",
    [
        # fmt: off
        ("y", True),
        ("yes", True),
        ("Y", True),
        ("YES", True),
        ("Yes", True),
        ("n", False),
        ("no", False),
        ("N", False),
        ("NO", False),
        pytest.param("normal_string", "normal_string", id="Normal strings remain unchanged"),
        pytest.param("123", "123", id="Numeric strings remain unchanged"),
        # fmt: on
    ],
)
def test_to_boolean(value, expected):
    assert to_boolean(value) == expected


@pytest.mark.parametrize(
    "value, key, expected",
    [
        # fmt: off
        pytest.param("asdf", None, "asdf", id="Strings remain unchanged"),
        pytest.param("23", None, 23, id="Integers get converted"),
        pytest.param("2.3", None, 2.3, id="Floats get converted"),
        pytest.param("2.3", None, 2.3, id="Floats get converted"),
        pytest.param("2014-05-26T14:10:31Z", "file_date", pendulum.datetime(2014, 5, 26, 14, 10, 31), id="Datetimes get converted",),
        pytest.param("2014-05-26", "date_acquired", pendulum.datetime(2014, 5, 26), id="Dates get converted",),
        pytest.param("09:10:26.7368720Z", "scene_center_time", pendulum.time(9, 10, 26, 736_872), id="Timestamps get converted",),
        # fmt: on
    ],
)
def test_to_python(value, key, expected):
    assert to_python(value, key) == expected


@pytest.mark.parametrize("value", NULL_VALUES)
def test_to_python_null_values(value):
    assert to_python(value) is None
