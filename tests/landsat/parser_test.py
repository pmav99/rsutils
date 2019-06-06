from pathlib import Path

from pendulum import Date, Time

import pytest

from rsutils.landsat.parser import parse_mtl

from .. import LANDSAT_MTL_FILES


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
