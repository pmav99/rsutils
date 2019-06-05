import importlib
import pathlib
from pprint import pprint as pp


import rsutils.landsat as landsat


mtl = pathlib.Path("tests/data/LC08_L1TP_204052_20190504_20190520_01_T1_MTL.txt")

sc = landsat.LS8_Metadata.from_path(mtl)
