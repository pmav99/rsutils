import pytest

from rsutils.landsat.parser import parse_mtl
from rsutils.landsat.metadata import (
    LS8_Coords,
    LS8_Metadata,
    LS8_Band,
    LS8_ThermalBand,
    LS8_QABand,
    LS8_Radiance,
    LS8_Reflectance,
)
from .. import LANDSAT_8_FILES


@LANDSAT_8_FILES
def test_landasat_8_instance_creation(global_datadir, mtl_filename):
    ls8 = LS8_Metadata.from_path(global_datadir / mtl_filename)
    assert ls8.row > 1
    assert ls8.path > 1
    assert isinstance(ls8.metadata, dict)
    assert isinstance(ls8.path, int)
    assert isinstance(ls8.row, int)
    assert isinstance(ls8.ul, LS8_Coords)
    assert isinstance(ls8.ur, LS8_Coords)
    assert isinstance(ls8.ll, LS8_Coords)
    assert isinstance(ls8.lr, LS8_Coords)
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
    assert isinstance(ls8.qa, LS8_QABand)


@LANDSAT_8_FILES
def test_get_landsat_qa_band(global_datadir, mtl_filename):
    metadata = parse_mtl(global_datadir / mtl_filename, convert=True)
    qa_band = LS8_QABand.from_meta(metadata)
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
    thermal_band = LS8_ThermalBand.from_meta(metadata, band_index)
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
    thermal_band = LS8_Band.from_meta(metadata, band_index)
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
    thermal_band = LS8_Band.from_meta(metadata, 8)
    assert isinstance(thermal_band, LS8_Band)
    assert thermal_band.index == 8
    assert thermal_band.filename == thermal_band.path.name
    assert not thermal_band.path.exists()
    assert thermal_band.height == metadata["panchromatic_lines"]
    assert thermal_band.width == metadata["panchromatic_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)
    assert isinstance(thermal_band.reflectance, LS8_Reflectance)
