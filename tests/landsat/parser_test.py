from pathlib import Path

from pendulum import Date, Time

import pytest

from rsutils.landsat import parse_mtl, LS8_Metadata, TileCoords, LS_Band, LS_ThermalBand


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
    ls8 = LS8_Metadata.from_mtl(global_datadir / mtl_filename)
    assert ls8.row > 1
    assert ls8.path > 1
    assert isinstance(ls8.metadata, dict)
    assert isinstance(ls8.path, int)
    assert isinstance(ls8.row, int)
    assert isinstance(ls8.ul, TileCoords)
    assert isinstance(ls8.ur, TileCoords)
    assert isinstance(ls8.ll, TileCoords)
    assert isinstance(ls8.lr, TileCoords)
    assert isinstance(ls8.b1, LS_Band)
    assert isinstance(ls8.b2, LS_Band)
    assert isinstance(ls8.b3, LS_Band)
    assert isinstance(ls8.b4, LS_Band)
    assert isinstance(ls8.b5, LS_Band)
    assert isinstance(ls8.b6, LS_Band)
    assert isinstance(ls8.b7, LS_Band)
    assert isinstance(ls8.b8, LS_Band)
    assert isinstance(ls8.b9, LS_Band)
    assert isinstance(ls8.b10, LS_ThermalBand)
    assert isinstance(ls8.b11, LS_ThermalBand)
