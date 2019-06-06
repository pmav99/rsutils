import pytest
import rasterio

from rsutils.landsat.parser import parse_mtl
from rsutils.landsat.metadata import (
    LS8_Coords,
    LS8_Metadata,
    LS8_BandBase,
    LS8_Band,
    LS8_ThermalBand,
    LS8_QABand,
    LS8_Radiance,
    LS8_Reflectance,
)
from .. import LANDSAT_8_FILES


@LANDSAT_8_FILES
def test_landasat_8_instance_creation(mtl_filename):
    ls8 = LS8_Metadata.from_path(mtl_filename)
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
def test_ls8_metadata_aliases(mtl_filename):
    ls8 = LS8_Metadata.from_path(mtl_filename)
    assert ls8.aerosol == ls8.b1
    assert ls8.coastal == ls8.b1
    assert ls8.blue == ls8.b2
    assert ls8.green == ls8.b3
    assert ls8.red == ls8.b4
    assert ls8.nir == ls8.b5
    assert ls8.swir1 == ls8.b6
    assert ls8.swir2 == ls8.b7
    assert ls8.pan == ls8.b8
    assert ls8.cirrus == ls8.b9
    assert ls8.tir1 == ls8.b10
    assert ls8.tir2 == ls8.b11


@LANDSAT_8_FILES
def test_ls8_qa_band(mtl_filename):
    metadata = parse_mtl(mtl_filename, convert=True)
    qa_band = LS8_QABand.from_meta(metadata)
    assert isinstance(qa_band, LS8_QABand)
    assert qa_band.index == 0
    assert qa_band.filename == qa_band.path.name
    assert qa_band.height == metadata["reflective_lines"]
    assert qa_band.width == metadata["reflective_samples"]


@pytest.mark.parametrize("band_index", (10, 11))
@LANDSAT_8_FILES
def test_ls8_thermal_band(mtl_filename, band_index):
    metadata = parse_mtl(mtl_filename, convert=True)
    thermal_band = LS8_ThermalBand.from_meta(metadata, band_index)
    assert isinstance(thermal_band, LS8_ThermalBand)
    assert thermal_band.index == band_index
    assert thermal_band.filename == thermal_band.path.name
    assert thermal_band.height == metadata["thermal_lines"]
    assert thermal_band.width == metadata["thermal_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)


@pytest.mark.parametrize("band_index", [1, 2, 3, 4, 5, 6, 7, 9])
@LANDSAT_8_FILES
def test_ls8_band(mtl_filename, band_index):
    metadata = parse_mtl(mtl_filename, convert=True)
    thermal_band = LS8_Band.from_meta(metadata, band_index)
    assert isinstance(thermal_band, LS8_Band)
    assert thermal_band.index == band_index
    assert thermal_band.filename == thermal_band.path.name
    assert thermal_band.height == metadata["reflective_lines"]
    assert thermal_band.width == metadata["reflective_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)
    assert isinstance(thermal_band.reflectance, LS8_Reflectance)


@LANDSAT_8_FILES
def test_ls8_panchromatic_band(mtl_filename):
    metadata = parse_mtl(mtl_filename, convert=True)
    thermal_band = LS8_Band.from_meta(metadata, 8)
    assert isinstance(thermal_band, LS8_Band)
    assert thermal_band.index == 8
    assert thermal_band.filename == thermal_band.path.name
    assert thermal_band.height == metadata["panchromatic_lines"]
    assert thermal_band.width == metadata["panchromatic_samples"]
    assert isinstance(thermal_band.radiance, LS8_Radiance)
    assert isinstance(thermal_band.reflectance, LS8_Reflectance)


class Test_LS8_BandBase:
    def test_get_src(self, ls8_scene_mtl):
        metadata = parse_mtl(ls8_scene_mtl, convert=True)
        band = LS8_BandBase.from_meta(metadata, 1)
        src = band.get_src()
        assert isinstance(src, rasterio.io.DatasetReader)
