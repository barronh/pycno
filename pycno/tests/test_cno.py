from .. import cno
import matplotlib.pyplot as plt
import numpy as np
import warnings


def test_cno_default():
    plt.close()
    warnings.simplefilter('ignore')
    ol = cno()
    warnings.resetwarnings()
    ol.draw()
    ax = plt.gca()
    nc = len(ax.collections)
    assert(nc == 1)


def test_cno_axkw():
    plt.close()
    ol = cno(data='.')
    fig, axx = plt.subplots(1, 3)
    ol.draw(ax=axx[1])
    assert(np.allclose(
        [0, 1, 0],
        [len(ax.collections) for ax in axx]
    ))


def test_cno_xylimkw():
    plt.close()
    ol = cno(xlim=(-180, 180), ylim=(-90, 90), data='.')
    ol.draw()
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    assert(xlim[0] == -180)
    assert(xlim[1] == 180)
    assert(ylim[0] == -90)
    assert(ylim[1] == 90)


def test_cno_projlcc():
    import pyproj
    proj = pyproj.Proj(
      (
        '+proj=lcc +lat_0=40 +lon_0=-97 +lat_1=33 +lat_2=45 ' +
        '+x_0=2412000 +y_0=1620000 +R=6370000 +to_meter=12000 ' +
        '+no_defs'
      ),
      preserve_units=True
    )
    plt.close()
    ol = cno(proj=proj, xlim=(0, 396), ylim=(0, 246), data='.')
    ol.draw()
    ax = plt.gca()
    nc = len(ax.collections)
    assert(nc == 1)


def test_cno_projps():
    import pyproj
    proj = pyproj.Proj(
      (
        '+proj=stere +lat_0=90 +lat_ts=45 +lon_0=-98 ' +
        '+x_0=10098000 +y_0=10098000 +R=6370000 +to_meter=108000 ' +
        '+no_defs'
      ),
      preserve_units=True
    )
    plt.close()
    ol = cno(proj=proj, xlim=(0, 187), ylim=(0, 187), data='.')
    ol.draw()
    ax = plt.gca()
    nc = len(ax.collections)
    assert(nc == 1)

def test_cno_cnofile():
    plt.close()
    ax = plt.gca()
    ol = cno(xlim=(-180, 180), ylim=(-90, 90))
    l = ol.draw('test.cno', ax=ax)
    p1, p2 = l.get_paths()
    xy1 = p1.vertices
    xy2 = p2.vertices
    assert((xy1[:, 0] == np.array([-4.0, -4., 4., 4., -4.])).all())
    assert((xy1[:, 1] == np.array([4.0, -4., -4., 4., 4.])).all())
    assert((xy2[:, 0] == np.array([-8.0, -8., 8., 8., -8.])).all())
    assert((xy2[:, 1] == np.array([8.0, -8., -8., 8., 8.])).all())

def test_cnob_cnofile():
    plt.close()
    ax = plt.gca()
    ol = cno(xlim=(-180, 180), ylim=(-90, 90))
    l = ol.draw('test.cnob', ax=ax)
    p1, p2 = l.get_paths()
    xy1 = p1.vertices
    xy2 = p2.vertices
    assert((xy1[:, 0] == np.array([-4.0, -4., 4., 4., -4.])).all())
    assert((xy1[:, 1] == np.array([4.0, -4., -4., 4., 4.])).all())
    assert((xy2[:, 0] == np.array([-8.0, -8., 8., 8., -8.])).all())
    assert((xy2[:, 1] == np.array([8.0, -8., -8., 8., 8.])).all())
