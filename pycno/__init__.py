__all__ = ['cno', 'downloadable', 'util', 'show_version', '__version__']
__doc__ = """Light-weight map-overlay drawing software

pycno
=====

Python map overlay software to read CNO and CNOB files. This provides a
light-weight interface to add overlays to `matplotlib` plots. For
longitude/latitude plots, no additional prerequisites are required. For data
with projected coordinates, see "projection support." This allows for pure
python installation with supplemental support if desired.

status
------

[Build status](https://travis-ci.org/barronh/pycno)
![Build badge](https://travis-ci.org/barronh/pycno.svg?branch=main)

Early development. Useful light weight mapping library. Expect enhancements.

install
-------

* Latest release: `pip install pycno`
* Lastest dev: `pip install https://github.com/barronh/pycno/archive/main.zip`


example usage
-------------

By default, this adds coasts and countries to the current axes. If the current
axes has no other data on it, provide the xlim/ylim keywords to define the
extents.

```
import pycno
import matplotlib.pyplot as plt


cno = pycno.cno(xlim=(-180, 180), ylim=(-90, 90))
cno.draw()
plt.savefig('coasts_countries.png')
```

Use the cnopath keyword to specify another overlay. If you specify a
downloadable cnopath you don't have, it will automatically be downloaded. For a
list of downloadable cnob, see pycno.downloadable. Currently, this includes the
[Panoply Overlay cnobs](https://www.giss.nasa.gov/tools/panoply/overlays/). For
example, `cno.draw('MWDB_Coasts_NA_1.cnob')` will download a high-resolution
version of North American coasts, continents, and states.


projection support
------------------

`pycno.cno` supports the pyproj projections. If you provide the `proj` keyword,
then overlays coordinates will be converted to the projection space before
being plotted. In this case, the xlim/ylim keyworkds will need to be provided
in projection space. This should work for most projections, but has only been
tested with  Lambert Conformal Conic and Polar Stereographic. If you test it
with another projection, please post a comment under issues and let us know.


lambert conic conformal
-----------------------

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


polar stereographic
-------------------

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


structure
=========

pycno
|-- __version__
|-- cno
|-- downloadable
|-- util
|   `-- shp2cno
`-- tests

* `cno` is the primary class
* `__version__` tells which MAJOR.MINOR.MICRO revision you are using
* `downloadable` dictionary of downloadable CNOB. Currently includes all
  [Panoply Overlays](https://www.giss.nasa.gov/tools/panoply/overlays/)
* `util` has some utilities for making cno and cnob files
* `tests` built-in test cases.
"""

import os
from pathlib import Path
import warnings
import numpy as np
from . import util

__version__ = "0.2.1"

_panoplyurl = 'https://www.giss.nasa.gov/tools/panoply/overlays/'
_panoplycnobs = [
    'MWDB_Coasts_1.cnob',
    'MWDB_Coasts_3.cnob',
    'MWDB_Coasts_Countries_1.cnob',
    'MWDB_Coasts_Countries_3.cnob',
    'MWDB_Coasts_Lakes_1.cnob',
    'MWDB_Coasts_Lakes_3.cnob',
    'MWDB_Coasts_NA_1.cnob',
    'MWDB_Coasts_NA_3.cnob',
    'MWDB_Coasts_USA_1.cnob',
    'MWDB_Coasts_USA_3.cnob',
    'MWDB_Lakes_Rivers_1.cnob',
    'MWDB_Lakes_Rivers_3.cnob',
    'Earth_5x4.cnob',
    'Earth_10x8.cnob',
    'Paleo_Cretaceous_100Ma.cnob',
    'Paleo_Paleocene_56Ma.cnob',
    'Paleo_Sturtian_750Ma.cnob',
    'Venus_MR_6052km.cnob'
]

downloadable = {k: _panoplyurl + k for k in _panoplycnobs}


def show_version():
    print(f'pycno: {__version__}')
    print('data store:', _getdata())
    try:
        import pyproj
        pyproj.show_versions()
    except Exception as e:
        print('Unable to print pyproj version', e)


def _getdata(data=None):
    if data is None:
        data = os.environ.get('PYCNO_DATA', None)

    if data is None:
        data = Path.home() / '.pycno'

    if not os.path.exists(data):
        warnings.warn('Path does not exist: ' + str(data) + '; default .')
        warnings.filterwarnings(
            "ignore", category=UserWarning, module=__name__, lineno=47
        )
        data = '.'
    return data


class cno:
    def __init__(
        self, proj=None, xlim=(None, None), ylim=(None, None), clipax=True,
        data=None, **line_kwds
    ):
        """
        CNO and CNOB overlay reader and plotter.

        Arguments
        ---------
        proj : pyproj.Proj
            or any function that accepts lon, lat and returns x, y in axes
            data coordinates
        xlim : tuple
            length 2 tuple where values must be accepted by set_xlim. If None,
            all data is plotted. Otherwise, overlay lines are only plotted
            within the xlim.
        ylim : tuple
            length 2 tuple where values must be accepted by set_ylim. If None,
            all data is plotted. Otherwise, overlay lines are only plotted
            within the ylim.
        clipax : bool
            If True, use ax.set_xlim and ax.set_ylim with xlim and ylim
            parameters
        data : str
            Optional, path to downloaded cno files. Defaults to environmental
            variable PYCNO_DATA, if not defined, defaults to ${HOME}/.pycno.
            If neither path exists, defaults to .
        line_kwds : keywords
            passed to drawing of lines. linewidth defaults to 0.5, and
            linecolor defaults to black. All other properties default to
            standard matplotlib.pypplot.rcParams
        """
        if isinstance(proj, str):
            import pyproj
            proj = pyproj.Proj(proj)

        self._xlim = xlim
        self._ylim = ylim
        self._proj = proj
        self._clipax = clipax
        self._cachedfeatures = {}
        self._linedefaults = line_kwds.copy()
        self._linedefaults.setdefault('color', 'k')
        self._linedefaults.setdefault('linewidth', 0.5)
        data = _getdata(data)
        self._data = Path(data)

    @property
    def data(self):
        return self._data

    def getfeatures(self, cnopath, cache=True, key=None):
        """
        Get coordinates for each feature.

        Arguments
        ---------
        cnopath : str
            path to file to plot. Will be evaluated as an absolute or relative
            path. Relative paths will be evaluated in the context of the
            working directory (`.`), the `data` path or `${HOME}/.pycno`.
            For a list of downloadable cnob, look at `pycno.downloadable`
        cache : bool
            store a cache for later reference
        key : str or None
            short name (default cnopath) for later reference

        Returns
        -------
        features : list
            list of features where each feature is (x, y)
        """
        if key is None:
            key = cnopath

        if cnopath in self._cachedfeatures:
            out = self._cachedfeatures[cnopath]
        else:
            cnorealpath = self._getoverlay(cnopath)
            out = self._parseoverlay(cnorealpath)
            if cache:
                self._cachedfeatures[key] = out

        return out

    def draw(
        self, cnopath='MWDB_Coasts_Countries_3.cnob', ax=None, **line_kwds
    ):
        """
        Add overlay to axes from cno file.

        Arguments
        ---------
        cnopath : str
            path to file to plot. Will be evaluated as an absolute or relative
            path. Relative paths will be evaluated in the context of the
            working directory (`.`), the `data` path or `${HOME}/.pycno`.
            For a list of downloadable cnob, look at `pycno.downloadable`
        ax : matplotlib.axes.Axes
            Optional, specify axes for overlay.
        line_kwds : mappable
            keywords for drawing lines.

        Returns
        -------
        lines : list
            lines that were added to ax or plt.gca().
        """
        from matplotlib.collections import LineCollection
        line_kwds = line_kwds.copy()
        for k, v in self._linedefaults.items():
            if k not in line_kwds:
                line_kwds[k] = v

        if ax is None:
            import matplotlib.pyplot as plt
            ax = plt.gca()
        features = self.getfeatures(cnopath)
        # Switching from lines to LineCollection
        # for efficiency
        # lines = []
        # for flon, flat in features:
        #     l, = ax.plot(flon, flat, **line_kwds)
        #     lines.append(l)
        segs = [np.ma.array(lonlat).T for lonlat in features]
        lines = LineCollection(
            segs, **line_kwds
        )
        ax.add_collection(lines)
        if self._clipax:
            ax.set_xlim(*self._xlim)
            ax.set_ylim(*self._ylim)
        return lines

    def drawcoastlines(self, ax=None, resnum=3, **line_kwds):
        """
        Call draw with 'MWDB_Coasts_{resnum}.cnob'
        """
        cnopath = f'MWDB_Coasts_{resnum}.cnob'
        return self.draw(cnopath=cnopath, ax=ax, **line_kwds)

    def drawcountries(self, ax=None, resnum=3, **line_kwds):
        """
        Call draw with 'MWDB_Coasts_Countries_{resnum}.cnob'
        """
        cnopath = f'MWDB_Coasts_Countries_{resnum}.cnob'
        return self.draw(cnopath=cnopath, ax=ax, **line_kwds)

    def drawstates(self, ax=None, resnum=3, **line_kwds):
        """
        Call draw with 'MWDB_Coasts_NA_{resnum}.cnob'
        """
        cnopath = f'MWDB_Coasts_NA_{resnum}.cnob'
        return self.draw(cnopath=cnopath, ax=ax, **line_kwds)

    def _parseoverlay(self, cnopath):
        """
        Parse a cno file

        Arguments
        ---------
        cnopath : str
          path to CNO or CNOB path

        Returns
        -------
        features : list
          list of (lons, lats) tuples
        """
        suffix = cnopath.suffix
        if suffix == '.cno':
            freader = self._parsecno
        else:
            freader = self._parsecnob

        features = freader(cnopath)
        return features

    def _parsecno(self, cnopath):
        """
        Arguments
        ---------
        cnopath : str
            path to a CNO binary file

        Returns
        -------
        xys : list
            list of tuples where the first element is x and the second is y

        Notes
        -----
        The definition of these file format is understood by reading the
        files, so it is an operational definition.

        A CNO is a text file, where the data is stored as common deliminted
        longitude,latitude pairs on each line. Polygons are separated by
        lines with a single 9999 between.
        e.g., the lines below could be a stand-alone cno file.

        -15.80,28.00
        -15.67,27.75
        -15.33,27.83
        -15.37,28.08
        -15.67,28.17
        -15.80,28.00
        9999
        -14.25,28.08
        -13.83,28.25
        -13.83,28.83
        -14.25,28.33
        -14.25,28.08
        """
        import re
        import io
        import numpy as np

        cnodata = open(cnopath).read()
        cnochunks = re.compile('^9999$', re.M).split(cnodata)
        features = []
        for cnochunk in cnochunks:
            if cnochunk == '':
                continue
            iochunk = io.StringIO(cnochunk)
            lon, lat = np.loadtxt(iochunk, delimiter=',').reshape(-1, 2).T
            x, y = self._lonlat2xy(lon, lat)
            if x is None or y is None:
                continue
            else:
                features.append((x, y))

        return features

    def _parsecnob(self, cnopath):
        """
        Arguments
        ---------
        cnopath : str
            path to a CNO binary file

        Returns
        -------
        xys : list
            list of tuples where the first element is x and the second is y

        Notes
        -----
        The definition of these file format is understood by reading the
        files, so it is an operational definition.

        A CNOB is a binary file starts with a text header with 8 characters
        GISSCNOB followed by a block of binary data. The binary data is
        stored as big-endian integers where the value has been multiplied by
        1000 with longitude followed by latitude. For CNOB, each polygon is
        bounded by 999999 (start and end).
        """

        f = open(cnopath, 'rb')
        buff = np.frombuffer(f.read(), '>i')
        check = buff[:2].view('S8')[0] == b'GISSCNOB'
        if not check:
            warnings.warn('Is CNOB file good?')
        nines, = np.where(buff == 999999)
        starts = nines[:-1]
        ends = nines[1:]
        features = []
        for s, e in zip(starts, ends):
            mybuff = buff[s + 1:e]
            lon, lat = mybuff.reshape(-1, 2).T / 1000
            x, y = self._lonlat2xy(lon, lat)
            if x is None or y is None:
                continue
            else:
                features.append((x, y))

        f.close()
        return features

    def _lonlat2xy(self, lon, lat):
        xlim = self._xlim
        ylim = self._ylim
        if self._proj is None:
            x = lon
            y = lat
        else:
            x, y = self._proj(lon, lat)

        if xlim[0] is not None:
            x = np.ma.masked_less(x, xlim[0])
        if xlim[1] is not None:
            x = np.ma.masked_greater(x, xlim[1])
        if ylim[0] is not None:
            y = np.ma.masked_less(y, ylim[0])
        if ylim[1] is not None:
            y = np.ma.masked_greater(y, ylim[1])
        if np.ma.getmaskarray(x).all():
            x, y = None, None
        if np.ma.getmaskarray(y).all():
            x, y = None, None
        return x, y

    def _getoverlay(self, cnopath):
        """
        Find or download overlay representing cnopath

        Arguments
        ---------
        cnopath : str
          path to CNOB path, relative to self.data or absolute

        Returns
        -------
        realpath : pathlib.Path
          realpath to cno file
        """

        from urllib.request import urlretrieve

        cnopatho = Path(cnopath)
        datapatho = self._data / cnopatho
        distpatho = Path(__path__[0]) / Path('data') / cnopatho
        testedpaths = [cnopatho, datapatho, distpatho]

        for path in testedpaths:
            if path.exists():
                return path
        else:
            if cnopath in downloadable:
                url = downloadable[cnopath]
                warnings.warn('Downloading: ' + url + ' to ' + str(datapatho))
                urlretrieve(url, datapatho)
                return datapatho
            else:
                raise OSError(
                    "Path not found\n - " + '\n - '.join(
                        [str(p) for p in testedpaths]
                    )
                )
