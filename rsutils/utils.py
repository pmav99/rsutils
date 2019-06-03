import ast
import logging
import pathlib
import typing

import pendulum
import pendulum.parsing.exceptions

logger = logging.getLogger(__name__)

NULL_VALUES = frozenset(("none", "None", "NONE", "null", "Null", "NULL"))

__all__ = [
    "NULL_VALUES",
    "_TO_PYTHON_DISPATCHER",
    "to_datetime",
    "to_time",
    "to_path",
    "ast_parser",
    "to_python",
]


def to_datetime(
    text: str, **kwargs  # pylint: disable=unused-argument
) -> pendulum.DateTime:
    """
    Convert `text` to `Date/DateTime` objects using `pendulum.parse`.
    If that fails return the object unchanged.
    """
    try:
        dt = pendulum.parse(text)
    except pendulum.exceptions.ParserError:
        logger.warning("pendulum: Failed to parse <%s>", text)
        dt = text
    return dt


def to_time(text: str, **kwargs) -> pendulum.Time:  # pylint: disable=unused-argument

    if text.endswith("Z"):
        text = text[:-1]
    if len(text) >= 15:
        text = text[:15]
    text, ms = text.split(".")
    ts = pendulum.Time(*map(int, text.split(":")), int(ms))
    return ts


def to_path(
    value: str, root_dir: pathlib.Path, **kwargs  # pylint: disable=unused-argument
) -> pathlib.Path:
    return root_dir / value


def ast_parser(
    value: str, **kwargs  # pylint: disable=unused-argument
) -> typing.Union[str, bytes, int, float, complex, tuple, list, dict, set, bool]:
    try:
        converted = ast.literal_eval(value)
    except (ValueError, SyntaxError, TypeError):
        # logger.warning("ast: Couldn't convert <%s>", value)
        converted = value
    return converted


_TO_PYTHON_DISPATCHER = {
    "file_date": to_datetime,
    "date_acquired": to_datetime,
    "scene_center_time": to_time,
    "file_name_band_1": to_path,
    "file_name_band_2": to_path,
    "file_name_band_3": to_path,
    "file_name_band_4": to_path,
    "file_name_band_5": to_path,
    "file_name_band_6": to_path,
    "file_name_band_6_vcid_1": to_path,
    "file_name_band_6_vcid_2": to_path,
    "file_name_band_7": to_path,
    "file_name_band_8": to_path,
    "file_name_band_9": to_path,
    "file_name_band_10": to_path,
    "file_name_band_11": to_path,
    "file_name_band_quality": to_path,
    "metadata_file_name": to_path,
    "ground_control_point_file_name": to_path,
}


def to_python(
    value: str,
    key: str = "",
    root_dir: typing.Union[pathlib.Path, None] = None,
    null_values: typing.Set[str] = NULL_VALUES,
) -> typing.Union[
    str,
    bytes,
    int,
    float,
    complex,
    tuple,
    list,
    dict,
    set,
    bool,
    None,
    pathlib.Path,
    pendulum.Date,
    pendulum.DateTime,
    pendulum.Time,
]:
    """
    Convert `value` to a python object using `ast.literal_eval`.

    If `value` is a `GRASS_NULL_VALUE` then return `None`.
    If `key` contains `date` or `time` convert to a pendulum datetime object.

    Parameters
    ----------
    value: str
        The value which we want to convert to a Python object.
    key: str
        The key whose corresponding value we want to convert to a Python object.

    """

    # Try conversions
    if value in null_values:
        converted = None
    else:
        func = _TO_PYTHON_DISPATCHER.get(key, ast_parser)
        converted = func(value, root_dir=root_dir)
    return converted
