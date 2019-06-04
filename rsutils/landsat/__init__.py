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
class TileCoords:
    lat: float
    lon: float
    x: float
    y: float


def get_landsat_coords(metadata: dict, corner: str) -> TileCoords:
    valid_corners = {"ul", "ur", "ll", "lr"}
    if corner not in valid_corners:
        raise ValueError(f"corner must be one of {valid_corners}, not: {corner}")
    coords = TileCoords(
        lat=metadata[f"corner_{corner}_lat_product"],
        lon=metadata[f"corner_{corner}_lon_product"],
        x=metadata[f"corner_{corner}_projection_x_product"],
        y=metadata[f"corner_{corner}_projection_y_product"],
    )
    return coords


@dataclasses.dataclass
class LS_Radiance:
    max: float
    min: float
    mult: float
    add: float


def get_landsat_radiance(metadata: dict, index: int) -> LS_radiance:
    radiance = LS_Radiance(
        max=metadata[f"radiance_maximum_band_{index}"],
        min=metadata[f"radiance_minimum_band_{index}"],
        mult=metadata[f"radiance_mult_band_{index}"],
        add=metadata[f"radiance_add_band_{index}"],
    )
    return radiance


@dataclasses.dataclass
class LS_Reflectance:
    max: float
    min: float
    mult: float
    add: float


def get_landsat_reflectance(metadata: dict, index: int) -> LS_Reflectance:
    reflectance = LS_Reflectance(
        max=metadata[f"reflectance_maximum_band_{index}"],
        min=metadata[f"reflectance_minimum_band_{index}"],
        mult=metadata[f"reflectance_mult_band_{index}"],
        add=metadata[f"reflectance_add_band_{index}"],
    )
    return reflectance


@dataclasses.dataclass
class LS_Band:
    filename: str
    path: pathlib.Path
    # XXX pixel_max or maybe just max?
    max: int
    min: int
    reflectance: LS_Reflectance
    radiance: LS_Radiance


def get_landsat_band(metadata: dict, index: int) -> LS_Band:
    if not (1 <= index <= 9):
        raise ValueError(f"Band index ∉ in [1, 9]: {index}")
    band = LS_Band(
        filename=metadata[f"file_name_band_{index}"].name,
        path=metadata[f"file_name_band_{index}"],
        max=metadata[f"quantize_cal_max_band_{index}"],
        min=metadata[f"quantize_cal_min_band_{index}"],
        reflectance=get_landsat_reflectance(metadata, index),
        radiance=get_landsat_radiance(metadata, index),
    )
    return band


@dataclasses.dataclass
class LS_ThermalBand:
    filename: str
    path: pathlib.Path
    max: int
    min: int
    radiance: LS_Radiance
    k1: float
    k2: float


def get_landsat_thermal_band(metadata: dict, index: int) -> LS_ThermalBand:
    if not (10 <= index <= 11):
        raise ValueError(f"Band index ∉ in [10, 11]: {index}")
    band = LS_ThermalBand(
        filename=metadata[f"file_name_band_{index}"].name,
        path=metadata[f"file_name_band_{index}"],
        max=metadata[f"quantize_cal_max_band_{index}"],
        min=metadata[f"quantize_cal_min_band_{index}"],
        radiance=get_landsat_radiance(metadata, index),
        k1=metadata[f"k1_constant_band_{index}"],
        k2=metadata[f"k2_constant_band_{index}"],
    )
    return band


@dataclasses.dataclass
class LS8_Metadata:
    # origin: str
    # request_id: str
    # scene_id: str
    # file_date: pendulum.DateTime
    # station_id: str
    # processing_software_version: str
    metadata: dict
    path: int
    row: int
    ll: TileCoords
    lr: TileCoords
    ul: TileCoords
    ur: TileCoords
    b1: LS_Band
    b2: LS_Band
    b3: LS_Band
    b4: LS_Band
    b5: LS_Band
    b6: LS_Band
    b7: LS_Band
    b8: LS_Band
    b9: LS_Band
    b10: LS_ThermalBand
    b11: LS_ThermalBand

    def __init__(self, metadata: dict) -> None:
        self.metadata = metadata
        self.path = metadata["wrs_path"]
        self.row = metadata["wrs_row"]
        self.ul = get_landsat_coords(metadata, "ul")
        self.ur = get_landsat_coords(metadata, "ur")
        self.ll = get_landsat_coords(metadata, "ll")
        self.lr = get_landsat_coords(metadata, "lr")
        self.b1 = get_landsat_band(metadata, 1)
        self.b2 = get_landsat_band(metadata, 2)
        self.b3 = get_landsat_band(metadata, 3)
        self.b4 = get_landsat_band(metadata, 4)
        self.b5 = get_landsat_band(metadata, 5)
        self.b6 = get_landsat_band(metadata, 6)
        self.b7 = get_landsat_band(metadata, 7)
        self.b8 = get_landsat_band(metadata, 8)
        self.b9 = get_landsat_band(metadata, 9)
        self.b10 = get_landsat_thermal_band(metadata, 10)
        self.b11 = get_landsat_thermal_band(metadata, 11)

    @classmethod
    def from_mtl(cls, mtl: pathlib.Path):
        metadata = parse_mtl(mtl, convert=True)
        instance = cls(metadata)
        return instance
