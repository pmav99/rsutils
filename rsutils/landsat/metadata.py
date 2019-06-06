""" Landsat Metadata """

from dataclasses import dataclass, field
import functools
import itertools
import logging
import pathlib
import typing

import numpy
import rasterio

from .parser import parse_mtl


logger = logging.getLogger(__name__)


@dataclass
class LS8_Coords:
    lat: float
    lon: float
    x: float
    y: float

    @classmethod
    def from_meta(cls, metadata: dict, corner: str) -> "LS8_Coords":
        valid_corners = {"ul", "ur", "ll", "lr"}
        if corner not in valid_corners:
            raise ValueError(f"corner must be one of {valid_corners}, not: {corner}")
        coords = cls(
            lat=metadata[f"corner_{corner}_lat_product"],
            lon=metadata[f"corner_{corner}_lon_product"],
            x=metadata[f"corner_{corner}_projection_x_product"],
            y=metadata[f"corner_{corner}_projection_y_product"],
        )
        return coords


@dataclass(order=False)
class LS8_BandDataBase:
    max: float
    min: float
    mult: float
    add: float


@dataclass(order=False)
class LS8_Reflectance(LS8_BandDataBase):
    @classmethod
    def from_meta(cls, metadata: dict, index: int) -> "LS8_Reflectance":
        reflectance = cls(
            max=metadata[f"reflectance_maximum_band_{index}"],
            min=metadata[f"reflectance_minimum_band_{index}"],
            mult=metadata[f"reflectance_mult_band_{index}"],
            add=metadata[f"reflectance_add_band_{index}"],
        )
        return reflectance


@dataclass(order=False)
class LS8_Radiance(LS8_BandDataBase):
    @classmethod
    def from_meta(cls, metadata: dict, index: int) -> "LS8_Radiance":
        radiance = cls(
            max=metadata[f"radiance_maximum_band_{index}"],
            min=metadata[f"radiance_minimum_band_{index}"],
            mult=metadata[f"radiance_mult_band_{index}"],
            add=metadata[f"radiance_add_band_{index}"],
        )
        return radiance


@dataclass(order=False)
class LS8_BandBase:
    index: int  # We assign 0 the QA band!
    filename: str
    path: pathlib.Path
    height: int
    width: int

    def to_numpy(self) -> numpy.ndarray:
        """ Open the TIFF and return a `numpy.ndarray` """
        with rasterio.open(self.path) as src:
            data = src.read(1)
        return data

    def get_src(self, *args, **kwargs):
        rio_open = functools.partial(rasterio.open, self.path)
        src = rio_open(*args, **kwargs)
        return src


@dataclass(order=False)
class LS8_QABand(LS8_BandBase):
    @classmethod
    def from_meta(cls, metadata: dict) -> "LS8_QABand":
        band = cls(
            index=0,
            filename=metadata["file_name_band_quality"].name,
            path=metadata["file_name_band_quality"],
            height=metadata["reflective_lines"],
            width=metadata["reflective_samples"],
        )
        return band


@dataclass(order=False)
class LS8_Band(LS8_BandBase):
    max: int
    min: int
    reflectance: LS8_Reflectance
    radiance: LS8_Radiance

    @classmethod
    def from_meta(cls, metadata: dict, index: int) -> "LS8_Band":
        if not (1 <= index <= 9):
            raise ValueError(f"Band index ∉ in [1, 9]: {index}")
        if index == 8:
            height = metadata["panchromatic_lines"]
            width = metadata["panchromatic_samples"]
        else:
            height = metadata["reflective_lines"]
            width = metadata["reflective_samples"]
        band = cls(
            index=index,
            filename=metadata[f"file_name_band_{index}"].name,
            path=metadata[f"file_name_band_{index}"],
            max=metadata[f"quantize_cal_max_band_{index}"],
            min=metadata[f"quantize_cal_min_band_{index}"],
            reflectance=LS8_Reflectance.from_meta(metadata, index),
            radiance=LS8_Radiance.from_meta(metadata, index),
            height=height,
            width=width,
        )
        return band


@dataclass(order=False)
class LS8_ThermalBand(LS8_BandBase):
    max: int
    min: int
    radiance: LS8_Radiance
    k1: float
    k2: float

    @classmethod
    def from_meta(cls, metadata: dict, index: int) -> "LS8_ThermalBand":
        if not (10 <= index <= 11):
            raise ValueError(f"Band index ∉ in [10, 11]: {index}")
        band = cls(
            index=index,
            filename=metadata[f"file_name_band_{index}"].name,
            path=metadata[f"file_name_band_{index}"],
            max=metadata[f"quantize_cal_max_band_{index}"],
            min=metadata[f"quantize_cal_min_band_{index}"],
            radiance=LS8_Radiance.from_meta(metadata, index),
            k1=metadata[f"k1_constant_band_{index}"],
            k2=metadata[f"k2_constant_band_{index}"],
            height=metadata["thermal_lines"],
            width=metadata["thermal_samples"],
        )
        return band


@dataclass(order=False)
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
    ll: LS8_Coords
    lr: LS8_Coords
    ul: LS8_Coords
    ur: LS8_Coords
    b1: LS8_Band
    b2: LS8_Band
    b3: LS8_Band
    b4: LS8_Band
    b5: LS8_Band
    b6: LS8_Band
    b7: LS8_Band
    b8: LS8_Band
    b9: LS8_Band
    b10: LS8_ThermalBand
    b11: LS8_ThermalBand
    qa: LS8_QABand
    # aliases
    coastal: LS8_Band = field(init=False)
    aerosol: LS8_Band = field(init=False)
    blue: LS8_Band = field(init=False)
    green: LS8_Band = field(init=False)
    red: LS8_Band = field(init=False)
    nir: LS8_Band = field(init=False)
    swir1: LS8_Band = field(init=False)
    swir2: LS8_Band = field(init=False)
    pan: LS8_Band = field(init=False)
    cirrus: LS8_Band = field(init=False)
    tir1: LS8_ThermalBand = field(init=False)
    tir2: LS8_ThermalBand = field(init=False)

    def __post_init__(self) -> None:
        # aliases
        self.coastal = self.b1
        self.aerosol = self.b1
        self.blue = self.b2
        self.green = self.b3
        self.red = self.b4
        self.nir = self.b5
        self.swir1 = self.b6
        self.swir2 = self.b7
        self.pan = self.b8
        self.cirrus = self.b9
        self.tir1 = self.b10
        self.tir2 = self.b11

    @classmethod
    def from_path(cls, mtl: pathlib.Path):
        metadata = parse_mtl(mtl, convert=True)
        instance = cls(
            metadata=metadata,
            path=metadata["wrs_path"],
            row=metadata["wrs_row"],
            ul=LS8_Coords.from_meta(metadata, "ul"),
            ur=LS8_Coords.from_meta(metadata, "ur"),
            ll=LS8_Coords.from_meta(metadata, "ll"),
            lr=LS8_Coords.from_meta(metadata, "lr"),
            b1=LS8_Band.from_meta(metadata, 1),
            b2=LS8_Band.from_meta(metadata, 2),
            b3=LS8_Band.from_meta(metadata, 3),
            b4=LS8_Band.from_meta(metadata, 4),
            b5=LS8_Band.from_meta(metadata, 5),
            b6=LS8_Band.from_meta(metadata, 6),
            b7=LS8_Band.from_meta(metadata, 7),
            b8=LS8_Band.from_meta(metadata, 8),
            b9=LS8_Band.from_meta(metadata, 9),
            b10=LS8_ThermalBand.from_meta(metadata, 10),
            b11=LS8_ThermalBand.from_meta(metadata, 11),
            qa=LS8_QABand.from_meta(metadata),
        )
        return instance

    def __iter__(self):
        return self.bands

    @property
    def bands(self):
        return iter(
            (
                self.b1,
                self.b2,
                self.b3,
                self.b4,
                self.b5,
                self.b6,
                self.b6,
                # self.b8,
                self.b9,
                self.b10,
                self.b11,
            )
        )

    def all_bands(self):
        itertools.chain(self.bands, iter(self.qa))

    @property
    def thermal_bands(self) -> typing.Iterator:
        return iter((self.b10, self.b11))

    @property
    def reflective_bands(self) -> typing.Iterator:
        return iter(
            (
                self.b1,
                self.b2,
                self.b3,
                self.b4,
                self.b5,
                self.b6,
                self.b6,
                self.b8,
                self.b9,
            )
        )

    def save_array(
        self, array: numpy.ndarray, path: typing.Union[pathlib.Path, str]
    ) -> None:
        path = pathlib.Path(path)
        if path.exists():
            raise ValueError(f"Path exists. Please provide a different one: {path}")
        rio_meta = self.rio_meta
        rio_meta.update({"dtype": array.dtype})
        with rasterio.open(path, "w", **rio_meta) as dst:
            dst.write_band(1, array)
