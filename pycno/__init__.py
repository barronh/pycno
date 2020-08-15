__all__ = ['cno']

import os
from pathlib import Path
import warnings
import numpy as np

class cno:
    def __init__(
        self, proj=None, xlim=(None, None), ylim=(None, None), clipax=True,
        data=None
    ):
        """
        CNO and CNOB overlay reader and plotter.

        Arguments
        ---------
        proj : pyproj.Proj
            or any function that accepts lon, lat, and inverse=True
        xlim : tuple
            length 2 tuple where values must be accepted by set_xlim
        ylim : tuple
            length 2 tuple where values must be accepted by set_ylim
        clipax : bool
            If True, use ax.set_xlim and ax.set_ylim with xlim and ylim 
            parameters
        data : str
            Optional, path to downloaded cno files. Defaults to environmental
            variable PYCNO_DATA, if not defined, defaults to .
        """
        if isinstance(proj, str):
            import pyproj
            proj = pyproj.Proj(proj)
        self._xlim = xlim
        self._ylim = ylim
        self._proj = proj
        self._clipax = clipax
        self._cachedfeatures = {}
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

    def getfeatures(self, cnopath):
        """
        Get coordinates for each feature.
        
        Arguments
        ---------
        cnopath : str
          path to cnob file
        
        Returns
        -------
        features : list
          list of features where each feature is (x, y)
        """
        if cnopath not in self._cachedfeatures:
            cnorealpath = self._getoverlay(cnopath)
            self._cachedfeatures[cnopath] = self._parseoverlay(cnorealpath)
        return self._cachedfeatures[cnopath]

    def draw(self, cnopath='MWDB_Coasts_Countries_3.cnob', ax=None):
        """
        Add overlay to axes from cno file.

        Arguments
        ---------
        cnopath : str
            path to file to plot
        ax : matplotlib.axes.Axes
            Optional, specify axes for overlay.

        Returns
        -------
        None
            lines are added to ax or plt.gca()
        """
        if ax is None:
            import matplotlib.pyplot as plt
            ax = plt.gca()
        features = self.getfeatures(cnopath)
        for flon, flat in features:
            ax.plot(flon, flat, color='k', linewidth=0.75, alpha=0.7)
        if self._clipax:
            ax.set_xlim(*self._xlim)
            ax.set_ylim(*self._ylim)

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
                x, y = self._proj(lon, lat, inverse)

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

        return features

    def _getoverlay(self, cnopath):
        """
        Find or download overlay representing cnopath

        Arguments
        ---------
        cnopath : str
          path to CNOB path, relative to self._data or absolute
        
        Returns
        -------
        realpath : pathlib.Path
          realpath to cno file
        """

        from urllib.request import urlretrieve
        cnopatho = Path(cnopath)
        if cnopatho.exists():
            return cnopatho
        cnopatho = self._data / cnopatho
        if not cnopatho.exists():
            panoplyurl = 'https://www.giss.nasa.gov/tools/panoply/overlays/'
            url = panoplyurl + cnopath
            warnings.warn('Downloading: ' + url + ' to ' + str(cnopatho))
            urlretrieve(url, cnopatho)
        return cnopatho
