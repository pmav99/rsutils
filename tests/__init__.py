import pathlib
import pytest


TEST_DIR = pathlib.Path(__file__).parent
ROOT_DIR = TEST_DIR.parent
DATA_DIR = TEST_DIR / "data"


LANDSAT_4_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        pytest.param(
            DATA_DIR / "LT04_L1TP_183035_19910901_20170126_01_T1_MTL.txt", id="ls4-new"
        )
    ],
)

LANDSAT_5_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        pytest.param(DATA_DIR / "LT51800342011158MOR00_MTL.txt", id="ls5-old"),
        pytest.param(
            DATA_DIR / "LT05_L1TP_038037_20120505_20160830_01_T1_MTL.txt", id="ls5-new"
        ),
    ],
)

LANDSAT_7_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        pytest.param(DATA_DIR / "LE71840332009140ASN00_MTL.txt", id="ls7-old"),
        pytest.param(
            DATA_DIR / "LE07_L1TP_016025_20190421_20190421_01_RT_MTL.txt", id="ls7-new"
        ),
    ],
)

LANDSAT_8_FILES = pytest.mark.parametrize(
    "mtl_filename",
    [
        pytest.param(DATA_DIR / "LC81840332014146LGN00_MTL.txt", id="ls8-old"),
        pytest.param(
            DATA_DIR / "LC08_L1TP_204052_20190504_20190520_01_T1_MTL.txt", id="ls8-new"
        ),
        pytest.param(
            DATA_DIR / "ls8" / "LC08_L1TP_204052_20190504_20190520_01_T1_DS_MTL.txt",
            id="ls8-downsampled",
        ),
    ],
)

LANDSAT_MTL_FILES = pytest.mark.parametrize(
    "mtl_filename",
    (
        []
        + LANDSAT_4_FILES.args[1]
        + LANDSAT_5_FILES.args[1]
        + LANDSAT_7_FILES.args[1]
        + LANDSAT_8_FILES.args[1]
    ),
)
