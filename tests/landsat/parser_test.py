from pathlib import Path

from pendulum import Date, Time

import pytest

from rsutils.landsat.parser import (
    parse_mtl,
    TileCoords,
    LS8_Metadata,
    LS8_Band,
    LS8_ThermalBand,
    LS8_QABand,
    LS8_Radiance,
    LS8_Reflectance,
    get_landsat_qa_band,
    get_landsat_band,
    get_landsat_thermal_band,
)


LANDSAT_4_FILES = pytest.mark.parametrize(
    "mtl_filename", ["LT04_L1TP_183035_19910901_20170126_01_T1_MTL.txt"]
)

LANDSAT_5_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        "LT51800342011158MOR00_MTL.txt",
        "LT05_L1TP_038037_20120505_20160830_01_T1_MTL.txt",
    ],
)

LANDSAT_7_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        "LE07_L1TP_016025_20190421_20190421_01_RT_MTL.txt",
        "LE71840332009140ASN00_MTL.txt",
    ],
)

LANDSAT_8_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        "LC81840332014146LGN00_MTL.txt",
        "LC08_L1TP_204052_20190504_20190520_01_T1_MTL.txt",
    ],
)

LANDSAT_MTL_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        "LT04_L1TP_183035_19910901_20170126_01_T1_MTL.txt",
        "LT51800342011158MOR00_MTL.txt",
        "LT05_L1TP_038037_20120505_20160830_01_T1_MTL.txt",
        "LE71840332009140ASN00_MTL.txt",
        "LE07_L1TP_016025_20190421_20190421_01_RT_MTL.txt",
        "LC81840332014146LGN00_MTL.txt",
    ],
)


@LANDSAT_MTL_FILES
def test_parse_mtl_no_conversion(global_datadir, mtl_filename):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=False)
    assert isinstance(metadata, dict)
    assert len(metadata) >= 100
    assert all("group" not in key for key in metadata.keys())
    assert all(isinstance(value, str) for value in metadata.values())


@LANDSAT_MTL_FILES
def test_parse_mtl_with_conversion(global_datadir, mtl_filename):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=True)
    assert isinstance(metadata, dict)
    assert len(metadata) >= 100
    assert all("group" not in key for key in metadata.keys())
    assert all(
        isinstance(value, (str, Path, float, int, Date, Time))
        for value in metadata.values()
    )
    assert isinstance(metadata["file_name_band_1"], Path)
    assert isinstance(metadata["file_name_band_2"], Path)
    assert isinstance(metadata["file_name_band_3"], Path)
    assert isinstance(metadata["file_name_band_4"], Path)
    assert isinstance(metadata["file_name_band_5"], Path)
    assert isinstance(metadata["file_date"], Date)
    assert isinstance(metadata["date_acquired"], Date)
    assert isinstance(metadata["scene_center_time"], Time)


@LANDSAT_8_FILES
def test_landasat_8_instance_creation(global_datadir, mtl_filename):
    ls8 = LS8_Metadata.from_path(global_datadir / mtl_filename)
    assert ls8.row > 1
    assert ls8.path > 1
    assert isinstance(ls8.metadata, dict)
    assert isinstance(ls8.path, int)
    assert isinstance(ls8.row, int)
    assert isinstance(ls8.ul, TileCoords)
    assert isinstance(ls8.ur, TileCoords)
    assert isinstance(ls8.ll, TileCoords)
    assert isinstance(ls8.lr, TileCoords)
    assert isinstance(ls8.b1, LS8_Band)
    assert isinstance(ls8.b2, LS8_Band)
    assert isinstance(ls8.b3, LS8_Band)
    assert isinstance(ls8.b4, LS8_Band)
    assert isinstance(ls8.b5, LS8_Band)
    assert isinstance(ls8.b6, LS8_Band)
    assert isinstance(ls8.b7, LS8_Band)
    assert isinstance(ls8.b8, LS8_Band)
    assert isinstance(ls8.b9, LS8_Band)
    assert isinstance(ls8.b10, LS8_ThermalBand)
    assert isinstance(ls8.b11, LS8_ThermalBand)


@LANDSAT_8_FILES
def test_get_landsat_qa_band(global_datadir, mtl_filename):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=True)
    qa_band = get_landsat_qa_band(metadata)
    assert isinstance(qa_band, LS8_QABand)
    assert qa_band.index == 0
    assert qa_band.filename == qa_band.path.name
    assert not qa_band.path.exists()
    assert qa_band.height == metadata["reflective_lines"]
    assert qa_band.width == metadata["reflective_samples"]


@pytest.mark.parametrize("band_index", (10, 11))
@LANDSAT_8_FILES
def test_get_landsat_thermal_band(global_datadir, mtl_filename, band_index):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=True)
    thermal_band = get_landsat_thermal_band(metadata, band_index)
    assert isinstance(thermal_band, LS8_ThermalBand)
    assert thermal_band.index == band_index
    assert thermal_band.filename == thermal_band.path.name
    assert not thermal_band.path.exists()
    assert thermal_band.height == metadata["thermal_lines"]
    assert thermal_band.width == metadata["thermal_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)


@pytest.mark.parametrize("band_index", [1, 2, 3, 4, 5, 6, 7, 9])
@LANDSAT_8_FILES
def test_get_landsat_band(global_datadir, mtl_filename, band_index):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=True)
    thermal_band = get_landsat_band(metadata, band_index)
    assert isinstance(thermal_band, LS8_Band)
    assert thermal_band.index == band_index
    assert thermal_band.filename == thermal_band.path.name
    assert not thermal_band.path.exists()
    assert thermal_band.height == metadata["reflective_lines"]
    assert thermal_band.width == metadata["reflective_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)
    assert isinstance(thermal_band.reflectance, LS8_Reflectance)


@LANDSAT_8_FILES
def test_get_landsat_panchromatic_band(global_datadir, mtl_filename):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=True)
    thermal_band = get_landsat_band(metadata, 8)
    assert isinstance(thermal_band, LS8_Band)
    assert thermal_band.index == 8
    assert thermal_band.filename == thermal_band.path.name
    assert not thermal_band.path.exists()
    assert thermal_band.height == metadata["panchromatic_lines"]
    assert thermal_band.width == metadata["panchromatic_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)
    assert isinstance(thermal_band.reflectance, LS8_Reflectance)
