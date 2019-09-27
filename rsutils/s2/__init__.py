import dataclasses
import pathlib
import typing

import lxml
import lxml.etree
import natsort


@dataclasses.dataclass
class S2BandData(object):
    path: pathlib.Path


@dataclasses.dataclass
class S2_R10(object):
    b02: S2BandData
    b03: S2BandData
    b04: S2BandData
    b08: S2BandData
    aot: S2BandData
    tci: S2BandData
    wvp: S2BandData


@dataclasses.dataclass
class S2_R20(object):
    b02: S2BandData
    b03: S2BandData
    b04: S2BandData
    b05: S2BandData
    b06: S2BandData
    b07: S2BandData
    b8a: S2BandData
    b11: S2BandData
    b12: S2BandData
    aot: S2BandData
    tci: S2BandData
    scl: S2BandData
    wvp: S2BandData


@dataclasses.dataclass
class S2_R60(object):
    b01: S2BandData
    b02: S2BandData
    b03: S2BandData
    b04: S2BandData
    b05: S2BandData
    b06: S2BandData
    b07: S2BandData
    b8a: S2BandData
    b11: S2BandData
    b12: S2BandData
    aot: S2BandData
    tci: S2BandData
    scl: S2BandData
    wvp: S2BandData


@dataclasses.dataclass
class S2Scene(object):
    r10: S2_R10
    r20: S2_R20
    r60: S2_R60

    b01: S2BandData
    b02: S2BandData
    b03: S2BandData
    b04: S2BandData
    b05: S2BandData
    b06: S2BandData
    b07: S2BandData
    b08: S2BandData
    b8a: S2BandData
    b11: S2BandData
    b12: S2BandData
    aot: S2BandData
    tci: S2BandData
    scl: S2BandData
    wvp: S2BandData

    @classmethod
    def from_manifest(cls, manifest: typing.Union[pathlib.Path, str]):
        manifest = pathlib.Path(manifest).expanduser().resolve()
        tree = lxml.etree.ElementTree(lxml.etree.XML(manifest.read_bytes()))
        datafiles = tree.xpath("//dataObjectSection[1]/dataObject[*]/byteStream[1]/fileLocation[1]/@href")
        img_data = natsort.natsorted([manifest / path for path in datafiles if "IMG_DATA" in path])
        r10 = S2_R10(**{key: S2BandData(path) for key, path in zip(("aot", "b02", "b03", "b04", "b08", "tci", "wvp"), img_data[:7])})
        r20 = S2_R20(**{key: S2BandData(path) for key, path in zip(("aot", "b02", "b03", "b04", "b05", "b06", "b07", "b8a", "b11", "b12", "scl", "tci", "wvp"), img_data[7:20])})
        r60 = S2_R60(**{key: S2BandData(path) for key, path in zip(("aot", "b01", "b02", "b03", "b04", "b05", "b06", "b07", "b8a", "b11", "b12", "scl", "tci", "wvp"), img_data[21:])})

        b01 = r60.b01
        b02 = r10.b02
        b03 = r10.b03
        b04 = r10.b04
        b05 = r60.b05
        b06 = r60.b06
        b07 = r60.b07
        b08 = r10.b08
        b8a = r60.b8a
        b11 = r60.b11
        b12 = r60.b12
        aot = r10.aot
        tci = r10.tci
        scl = r20.scl
        wvp = r10.wvp

        instance = cls(r10=r10, r20=r20, r60=r60, b01=b01, b02=b02, b03=b03, b04=b04, b05=b05, b06=b06, b07=b07, b08=b08, b8a=b8a, b11=b11, b12=b12, aot=aot, tci=tci, scl=scl, wvp=wvp)
        return instance
