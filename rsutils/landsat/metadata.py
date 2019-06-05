""" Landsat Metadata """


from dataclasses import dataclass, field
import logging
import pathlib

import numpy
import rasterio as rio

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


@dataclass
class TileCoords:
    lat: float
    lon: float
    x: float
    y: float


@dataclass(order=False)
class LS8_BandDataBase:
    max: float
    min: float


@dataclass(order=False)
class LS8_Reflectance(LS8_BandDataBase):
    mult: float
    add: float


@dataclass(order=False)
class LS8_Radiance(LS8_BandDataBase):
    mult: float
    add: float


@dataclass(order=False)
class LS8_BandBase:
    index: int  # We assign 0 the QA band!
    filename: str
    path: pathlib.Path
    height: int
    width: int

    def to_numpy(self) -> numpy.ndarray:
        """ Open the TIFF and return a `numpy.ndarray` """
        with rio.open(self.path) as src:
            data = src.read(1)
        return data


@dataclass(order=False)
class LS8_QABand(LS8_BandBase):
    pass


@dataclass(order=False)
class LS8_Band(LS8_BandBase):
    max: int
    min: int
    reflectance: LS8_Reflectance
    radiance: LS8_Radiance


@dataclass(order=False)
class LS8_ThermalBand(LS8_BandBase):
    max: int
    min: int
    radiance: LS8_Radiance
    k1: float
    k2: float


@dataclass(order=False)
class LS8_Metadata:
    # origin: str
    # request_id: str
    # scene_id: str
    # file_date: pendulum.DateTime
    # station_id: str
    # processing_software_version: str
    metadata: dict
    path: int = field(init=False)
    row: int = field(init=False)
    ll: TileCoords = field(init=False)
    lr: TileCoords = field(init=False)
    ul: TileCoords = field(init=False)
    ur: TileCoords = field(init=False)
    b1: LS8_Band = field(init=False)
    b2: LS8_Band = field(init=False)
    b3: LS8_Band = field(init=False)
    b4: LS8_Band = field(init=False)
    b5: LS8_Band = field(init=False)
    b6: LS8_Band = field(init=False)
    b7: LS8_Band = field(init=False)
    b8: LS8_Band = field(init=False)
    b9: LS8_Band = field(init=False)
    b10: LS8_ThermalBand = field(init=False)
    b11: LS8_ThermalBand = field(init=False)
    qa: LS8_QABand = field(init=False)
    # aliases
    pan: LS8_Band = field(init=False)
    red: LS8_Band = field(init=False)
    green: LS8_Band = field(init=False)
    blue: LS8_Band = field(init=False)
    nir: LS8_Band = field(init=False)
    swir1: LS8_Band = field(init=False)
    swir2: LS8_Band = field(init=False)
    t1: LS8_ThermalBand = field(init=False)
    t2: LS8_ThermalBand = field(init=False)

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
        self.qa = get_landsat_qa_band(metadata)
        # aliases
        self.blue = self.b2
        self.green = self.b3
        self.red = self.b4
        self.nir = self.b5
        self.swir1 = self.b6
        self.swir2 = self.b7
        self.pan = self.b8
        self.t1 = self.b10
        self.t2 = self.b11

    @classmethod
    def from_path(cls, mtl: pathlib.Path):
        metadata = parse_mtl(mtl, convert=True)
        instance = cls(metadata)
        return instance


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


def get_landsat_reflectance(metadata: dict, index: int) -> LS8_Reflectance:
    reflectance = LS8_Reflectance(
        max=metadata[f"reflectance_maximum_band_{index}"],
        min=metadata[f"reflectance_minimum_band_{index}"],
        mult=metadata[f"reflectance_mult_band_{index}"],
        add=metadata[f"reflectance_add_band_{index}"],
    )
    return reflectance


def get_landsat_radiance(metadata: dict, index: int) -> LS8_Radiance:
    radiance = LS8_Radiance(
        max=metadata[f"radiance_maximum_band_{index}"],
        min=metadata[f"radiance_minimum_band_{index}"],
        mult=metadata[f"radiance_mult_band_{index}"],
        add=metadata[f"radiance_add_band_{index}"],
    )
    return radiance


def get_landsat_band(metadata: dict, index: int) -> LS8_Band:
    if not (1 <= index <= 9):
        raise ValueError(f"Band index ∉ in [1, 9]: {index}")
    if index == 8:
        height = metadata["panchromatic_lines"]
        width = metadata["panchromatic_samples"]
    else:
        height = metadata["reflective_lines"]
        width = metadata["reflective_samples"]
    band = LS8_Band(
        index=index,
        filename=metadata[f"file_name_band_{index}"].name,
        path=metadata[f"file_name_band_{index}"],
        max=metadata[f"quantize_cal_max_band_{index}"],
        min=metadata[f"quantize_cal_min_band_{index}"],
        reflectance=get_landsat_reflectance(metadata, index),
        radiance=get_landsat_radiance(metadata, index),
        height=height,
        width=width,
    )
    return band


def get_landsat_thermal_band(metadata: dict, index: int) -> LS8_ThermalBand:
    if not (10 <= index <= 11):
        raise ValueError(f"Band index ∉ in [10, 11]: {index}")
    band = LS8_ThermalBand(
        index=index,
        filename=metadata[f"file_name_band_{index}"].name,
        path=metadata[f"file_name_band_{index}"],
        max=metadata[f"quantize_cal_max_band_{index}"],
        min=metadata[f"quantize_cal_min_band_{index}"],
        radiance=get_landsat_radiance(metadata, index),
        k1=metadata[f"k1_constant_band_{index}"],
        k2=metadata[f"k2_constant_band_{index}"],
        height=metadata["thermal_lines"],
        width=metadata["thermal_samples"],
    )
    return band


def get_landsat_qa_band(metadata: dict) -> LS8_QABand:
    band = LS8_QABand(
        index=0,
        filename=metadata["file_name_band_quality"].name,
        path=metadata["file_name_band_quality"],
        height=metadata["reflective_lines"],
        width=metadata["reflective_samples"],
    )
    return band
