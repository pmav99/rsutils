import importlib
import pathlib
import shutil

import pytest

from rsutils.landsat import parse_mtl, LS8_Metadata
from . import DATA_DIR


@pytest.fixture(scope="function")
def ls8_scene(tmp_path):
    """Return a temporary directory containing a copy of a downsampled LS8 scene."""
    src_dir = DATA_DIR / "ls8"
    for filename in src_dir.glob("*"):
        shutil.copy(filename, tmp_path)
    return tmp_path


@pytest.fixture(scope="function")
def ls8_scene_mtl(ls8_scene):
    """Return the path to the MTL of a temporary directory containing a copy of a downsampled LS8 scene."""
    print(ls8_scene)
    print(list(ls8_scene.glob("*MTL.txt")))
    mtl = next(ls8_scene.glob("*MTL.txt"))
    return mtl


@pytest.fixture(scope="function")
def ls8_scene_meta(ls8_scene_mtl):
    """ Return an instance of LS8_Metadata with the downsampled data """
    metadata = LS8_Metadata.from_path(ls8_scene_mtl, convert=True)
    return metadata
