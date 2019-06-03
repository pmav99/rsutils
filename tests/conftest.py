import importlib
import pathlib
import shutil


import pytest


@pytest.fixture
def global_datadir(tmpdir):
    package_name = __name__.split(".")[0]
    package_path = pathlib.Path(importlib.import_module(package_name).__file__).parent
    global_shared_path = package_path / "data"
    temp_path = pathlib.Path(str(tmpdir.join("data")))
    shutil.copytree(global_shared_path, temp_path)
    return temp_path
