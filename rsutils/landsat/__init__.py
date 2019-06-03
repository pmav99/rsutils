""" Landsat Metadata """

from __future__ import annotations

import dataclasses
import logging
import pathlib

import pendulum
import pendulum.parsing.exceptions

from ..utils import to_python


logger = logging.getLogger(__name__)


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
