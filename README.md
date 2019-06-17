![Azure Build status](https://img.shields.io/azure-devops/build/pmav99/rsutils/1.svg?style=plastic)
![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/pmav99/rsutils/1.svg?style=plastic)

rsutils
=======

An Object Oriented API for working with Remote Sensor Metadata.

This is a WIP. Currently only Landsat 8 is supported.

### Requirements

Python 3.6+

### API

#### Higher level API

``` python
import pathlib
import rsutils.landsat as landsat

scene = landsat.LS8_Metadata.from_path(
    pathlib.Path("tests/data/LC08_L1TP_204052_20190504_20190520_01_T1_MTL.txt"),
)


# The scene's WRS path/row:
print(scene.path)
print(scene.row)
print()

# The scene's coords both in lat/lon and unprojected form:
print(scene.ul.lat)
print(scene.ll.lon)
print(scene.ur.x)
print(scene.ul.y)
print()

# You can access the scene's band using b + the index of each band. E.g.:
print(scene.b1)
print(scene.b8)
print(scene.b11)
print()

# You can also use certain common aliases:
print(scene.red)
print(scene.green)
print(scene.blue)
print(scene.nir)
print(scene.swir1)
print(scene.swir2)
print(scene.pan)
print(scene.qa)
print()

# Each band has it's own attributes. E.g:
print(scene.b1.filename)
print(scene.b2.path)
print()


# index is the band index number. We assign 0 to the QA band
print(scene.b3.index)
print(scene.b11.index)
print(scene.qa.index)
print()

# num of rows and columns
# Note: the panchromatic band has more rows than the ordinary ones + the thermal bands
# might also have different values.
print(scene.b3.height)
print(scene.b3.width)
print(scene.b8.height)
print(scene.b8.width)
print()

# A band's min and max DN values
print(scene.b4.max)
print(scene.b5.min)
print()

# A band's radiance data
print(scene.b7.radiance.max)
print(scene.b7.radiance.min)
print(scene.b7.radiance.add)
print(scene.b7.radiance.mult)
print()

# A band's reflectance data
print(scene.b7.reflectance.max)
print(scene.b7.reflectance.min)
print(scene.b7.reflectance.add)
print(scene.b7.reflectance.mult)
print()

# Thermal bands don't have reflectance but they have k1, k2 coeffs too
print(scene.b10.radiance.max)
print(scene.b10.radiance.min)
print(scene.b10.radiance.add)
print(scene.b10.radiance.mult)
print(scene.b11.k1)
print(scene.b11.k2)
print()
```

#### Lower level API

The `parse_mtl` function will return a dictionary. If `convert=True` then the values
will be casted to Python objects (integers, floats, booleans, `pathlib.Path`, None, etc)

``` python
import pathlib
import rsutils.landsat as landsat

metadata = landsat.parse_mtl(
    pathlib.Path("tests/data/LC08_L1TP_204052_20190504_20190520_01_T1_MTL.txt"),
    # convert=True,
)
```
