from __future__ import annotations

import ast
import dataclasses
import logging
import pathlib
import typing

import pendulum
import pendulum.parsing.exceptions

logger = logging.getLogger(__name__)

NULL_VALUES = {"none", "None", "NONE", "null", "Null", "NULL"}


def to_datetime(text: str, **kwargs) -> pendulum.DateTime:
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


def to_time(text: str, **kwargs) -> pendulum.Time:
    if text.endswith("Z"):
        text = text[:-1]
    if len(text) >= 15:
        text = text[:15]
    text, ms = text.split(".")
    ts = pendulum.Time(*map(int, text.split(":")), int(ms))
    return ts


def ast_parser(
    value: str, **kwargs
) -> typing.Union[str, bytes, int, float, complex, tuple, list, dict, set, bool]:
    try:
        converted = ast.literal_eval(value)
    except (ValueError, SyntaxError, TypeError):
        # logger.warning("ast: Couldn't convert <%s>", value)
        converted = value
    return converted


def to_path(value: str, root_dir: pathlib.Path, **kwargs) -> pathlib.Path:
    return root_dir / value


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
    "file_name_band_7": to_path,
    "file_name_band_8": to_path,
    "file_name_band_9": to_path,
    "file_name_band_10": to_path,
    "file_name_band_11": to_path,
    "file_name_band_quality": to_path,
    "metadata_file_name": to_path,
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
        if key in _TO_PYTHON_DISPATCHER:
            func = _TO_PYTHON_DISPATCHER[key]
        else:
            func = ast_parser
        converted = func(value, root_dir=root_dir)
    return converted


def parse_mtl(mtl: pathlib.Path, convert=False) -> dict:
    """
    Parse the Metadata file and return a dictionary with the key-value pairs.
    Note: The keys are converted to lowercase.
    """
    # populate the dictionary with the key-value pairs.
    # skip "GROUP" lines and the last line (i.e. "END")
    metadata = {}
    if convert:
        root_dir = mtl.parent.resolve()
    with mtl.open() as fd:
        for i, line in enumerate(fd.readlines()[:-1], start=1):
            line = line.strip()
            if line and "GROUP = " not in line:
                try:
                    key, value = line.split(" = ")
                    key = key.lower()
                    value = value.replace('"', "")
                    if convert:
                        value = to_python(value, key, root_dir)
                except Exception:
                    logger.error("Problem in line %d: %s", i, line)
                    raise
                else:
                    metadata[key] = value
    return metadata


@dataclasses.dataclass
class LS8_MTL_Metadata:
    origin: str
    request_id: str
    scene_id: str
    file_date: pendulum.DateTime
    station_id: str
    processing_software_version: str


@dataclasses.dataclass
class LS8_MTL:
    metadata: LS8_MTL_Metadata

    """
    # clean and convert MTL lines in to a named tuple
    self.mtl = self._to_namedtuple(mtl_lines, 'metadata')
    self._set_attributes()

    # shorten LANDSAT_SCENE_ID, SENSOR_ID
    self.scene_id = self.mtl.LANDSAT_SCENE_ID
    self.sensor = self.mtl.SENSOR_ID

    # bounding box related
    self.corner_ul = (self.mtl.CORNER_UL_LAT_PRODUCT,
                        self.mtl.CORNER_UL_LON_PRODUCT)
    self.corner_lr = (self.mtl.CORNER_LR_LAT_PRODUCT,
                        self.mtl.CORNER_LR_LON_PRODUCT)
    self.corner_ul_projection = (self.mtl.CORNER_UL_PROJECTION_X_PRODUCT,
                                    self.mtl.CORNER_UL_PROJECTION_Y_PRODUCT)
    self.corner_lr_projection = (self.mtl.CORNER_LR_PROJECTION_X_PRODUCT,
                                    self.mtl.CORNER_LR_PROJECTION_Y_PRODUCT)
    self.cloud_cover = self.mtl.CLOUD_COVER
    """
