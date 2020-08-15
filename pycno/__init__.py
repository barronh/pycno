__all__ = ['cno']

import os
import numpy as np

class cno:
    def __init__(
        self, proj=None, xlim=(None, None), ylim=(None, None), clipax=True
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
        clipax: bool
            If True, use ax.set_xlim and ax.set_ylim with xlim and ylim parameters
        """
        if isinstance(proj, str):
            import pyproj
            proj = pyproj.Proj(proj)
        self._xlim = xlim
        self._ylim = ylim
        self._proj = proj
        self._clipax = clipax
        self._cachedfeatures = {}
    
    def getfeatures(self, cnobpath):
        """
        Get coordinates for each feature.
        
        Arguments
        ---------
        cnobpath : str
          path to cnob file
        
        Returns
        -------
        features : list
          list of features where each feature is (x, y)
        """
        if cnobpath not in self._cachedfeatures:
            if not os.path.exists(cnobpath):
                cno._getoverlay(cnobpath)
            self._cachedfeatures[cnobpath] = self._parseoverlay(cnobpath)
        return self._cachedfeatures[cnobpath]

    def draw(self, cnobpath='MWDB_Coasts_Countries_3.cnob', ax=None):
        if ax is None:
            import matplotlib.pyplot as plt
            ax = plt.gca()
        features = self.getfeatures(cnobpath)
        for flon, flat in features:
            ax.plot(flon, flat, color='k', linewidth=0.75, alpha=0.7)
        if self._clipax:
            ax.set_xlim(*self._xlim)
            ax.set_ylim(*self._ylim)

    def _parseoverlay(self, cnobpath):
        """
        Arguments
        ---------
        cnobpath : str
          path to CNOB path
        
        Returns
        -------
        features : list
          list of (lons, lats) tuples
        """
        f = open(cnobpath, 'rb')
        buff = np.frombuffer(f.read(), '>i')
        check = buff[:2].view('S8')[0] == b'GISSCNOB'
        if not check:
            print('Is CNOB file good?')
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

    @classmethod
    def _getoverlay(cls, cnobpath):
        from urllib.request import urlretrieve
        urlretrieve('https://www.giss.nasa.gov/tools/panoply/overlays/' + cnobpath, cnobpath)
    
