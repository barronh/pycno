__all__ = ['cno', 'downloadable', 'version']

import os
from pathlib import Path
import warnings
import numpy as np


__version__ = "0.1.1"

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
            length 2 tuple where values must be accepted by set_xlim
        ylim : tuple
            length 2 tuple where values must be accepted by set_ylim
        clipax : bool
            If True, use ax.set_xlim and ax.set_ylim with xlim and ylim
            parameters
        data : str
            Optional, path to downloaded cno files. Defaults to environmental
            variable PYCNO_DATA, if not defined, defaults to ${HOME}/.pycno.
            If neither path exists, defaults to .
        line_kwds : keywords
            passed to drawing of lines. linewidth defaults to 0.5, and
            linecolor defaults to black. All other properties defautl to
            rcParams
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

    def _parseoverlay(self, cnopath):
        """
        Parse a cno file

        Arguments
        ---------
        cnopath : str
          path to CNOB path

        Returns
        -------
        features : list
          list of (lons, lats) tuples
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
        xlim = self._xlim
        ylim = self._ylim
        for s, e in zip(starts, ends):
            mybuff = buff[s + 1:e]
            lon, lat = mybuff.reshape(-1, 2).T / 1000
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
                continue
            if np.ma.getmaskarray(y).all():
                continue
            features.append((x, y))

        f.close()
        return features

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
