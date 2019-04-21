import pathlib

import pendulum
import pytest

from rsutils.landsat import to_python, NULL_VALUES, parse_mtl


@pytest.mark.parametrize(
    "value, key, expected",
    [
        # fmt: off
        pytest.param("asdf", None, "asdf", id="Strings remain unchanged"),
        pytest.param("23", None, 23, id="Integers get converted"),
        pytest.param("2.3", None, 2.3, id="Floats get converted"),
        pytest.param("2.3", None, 2.3, id="Floats get converted"),
        pytest.param("2014-05-26T14:10:31Z", "file_date", pendulum.datetime(2014, 5, 26, 14, 10, 31), id="Datetimes get converted",),
        pytest.param("2014-05-26", "date_acquired", pendulum.date(2014, 5, 26), id="Dates get converted",),
        pytest.param("09:10:26.7368720Z", "scene_center_time", pendulum.time(9, 10, 26, 736_872), id="Timestamps get converted",),
        # fmt: on
    ],
)
def test_to_python(value, key, expected):
    to_python(value, key) == expected


@pytest.mark.parametrize("value", NULL_VALUES)
def test_to_python_null_values(value):
    to_python(value) is None


@pytest.mark.parametrize("filename", ["mtl.txt"])
def test_parse_mtl_without_conversion(shared_datadir, filename):
    metadata = parse_mtl(shared_datadir / filename)
    assert isinstance(metadata, dict)
    assert len(metadata) == 185
    assert all("group" not in key for key in metadata.keys())
    assert all(isinstance(value, str) for value in metadata.values())


@pytest.mark.parametrize("filename", ["mtl.txt"])
def test_parse_mtl_with_conversion(shared_datadir, filename):
    metadata = parse_mtl(shared_datadir / filename, convert=True)
    assert isinstance(metadata, dict)
    assert len(metadata) == 185
    # check paths conversions
    paths = [
        (key, value)
        for (key, value) in metadata.items()
        if "file_name_band" in key or "metadata_file_name" in key
    ]
    for (key, value) in paths:
        assert isinstance(value, pathlib.Path), f"Problem in path conversion: {key}"
    # check date conversion
    date_items = [(key, value) for (key, value) in metadata.items() if "date" in key]
    for key, value in date_items:
        # breakpoint()
        assert isinstance(
            value, pendulum.DateTime
        ), f"Problem in date conversion: {key}"
    # check time conversion
    time_items = [(key, value) for (key, value) in metadata.items() if "time" in key]
    for key, value in time_items:
        assert isinstance(value, pendulum.Time), f"Problem in time conversion: {key}"
