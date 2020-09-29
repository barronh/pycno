# pycno

Python map overlay software to read CNO and CNOB files. This provides a light-weight interface to add overlays to `matplotlib` plots. For longitude/latitude plots, no additional prerequisites are required. For projections, see "projection support." This allows for pure python installation with supplemental support if desired.

# status

[![Build Status](https://travis-ci.org/barronh/pycno.svg?branch=main)](https://travis-ci.org/barronh/pycno)

Early development. Useful light weight mapping library. Interface may change.

# install 

* Latest release: `pip install pycno`
* Lastest development: `pip install https://github.com/barronh/pycno/archive/main.zip`


# example usage

By default, this adds coasts and countries to the current axes. If the current axes has no other data on it, provide the xlim/ylim keywords to define the extents.

```
import pycno
import matplotlib.pyplot as plt


cno = pycno.cno(xlim=(-180, 180), ylim=(-90, 90))
cno.draw()
plt.savefig('coasts_countries.png')
```

Use the cnopath keyword to specify another overlay. If you specify a downloadable cnopath you don't have, it will automatically be downloaded. For a list of downloadable cnob, see pycno.downloadable. Currently, this includes the [Panoply Overlay cnobs](https://www.giss.nasa.gov/tools/panoply/overlays/). For example, `cno.draw('MWDB_Coasts_NA_1.cnob')` will download a high-resolution version of North American coasts, continents, and states.

# projection support

`pycno.cno` supports the pyproj projections. If you provide proj, then overlays will be converted to the projection space and xlim/ylim will need to be provided in projection space. This should work for most projections, but has only been tested with  Lambert Conformal Conic and Polar Stereographic. If you test it with another projection, please post a comment under issues and let us know.


## lambert conic conformal

Example uses LCC domain used by EPA and called 12US2

```
import pycno
import pyproj
import matplotlib.pyplot as plt


proj = pyproj.Proj(
  (
    '+proj=lcc +lat_0=40 +lon_0=-97 +lat_1=33 +lat_2=45 ' +
    '+x_0=2412000 +y_0=1620000 +R=6370000 +to_meter=12000 ' +
    '+no_defs'
  ),
  preserve_units=True
)
plt.axis('image')
cno = pycno.cno(proj=proj, xlim=(0, 396), ylim=(0, 246))
cno.draw()
plt.savefig('coasts_countries_lcc.png')
```

## polar stereographic

Example uses Polar Stereographic domain used by EPA and called 108NHEMI2


```
import pycno
import pyproj
import matplotlib.pyplot as plt


proj = pyproj.Proj(
  (
    '+proj=stere +lat_0=90 +lat_ts=45 +lon_0=-98 ' +
    '+x_0=10098000 +y_0=10098000 +R=6370000 +to_meter=108000 ' +
    '+no_defs'
  ),
  preserve_units=True
)
plt.axis('image')
cno = pycno.cno(proj=proj, xlim=(0, 187), ylim=(0, 187))
cno.draw()
plt.savefig('coasts_countries_ps.png')
```
