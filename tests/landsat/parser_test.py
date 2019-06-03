from pathlib import Path

from pendulum import Date, Time

import pytest

from rsutils.landsat import parse_mtl


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

LANDSAT_7_FILES = pytest.mark.parametrize(
    "mtl_filename", ["LC81840332014146LGN00_MTL.txt"]
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