import importlib
import pathlib
from pprint import pprint as pp


import rsutils.landsat as landsat
import rsutils.s2 as sentinel2


mtl = pathlib.Path("tests/data/LC08_L1TP_204052_20190504_20190520_01_T1_MTL.txt")

sc = landsat.LS8_Metadata.from_path(mtl)

manifest = pathlib.Path("tests/data/manifest.safe")
s2 = sentinel2.S2Scene.from_manifest(manifest)
