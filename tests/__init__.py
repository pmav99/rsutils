import pytest


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
