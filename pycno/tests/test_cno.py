from .. import cno
import matplotlib.pyplot as plt
import numpy as np


def test_cno_default():
    plt.close()
    ol = cno()
    ol.draw()
    ax = plt.gca()
    nc = len(ax.collections)
    assert(nc == 1)


def test_cno_axkw():
    plt.close()
    ol = cno()
    fig, axx = plt.subplots(1, 3)
    ol.draw(ax=axx[1])
    assert(np.allclose(
        [0, 1, 0],
        [len(ax.collections) for ax in axx]
    ))


def test_cno_xylimkw():
    plt.close()
    ol = cno(xlim=(-180, 180), ylim=(-90, 90))
    ol.draw()
    ax = plt.gca()
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    assert(xlim[0] == -180)
    assert(xlim[1] == 180)
    assert(ylim[0] == -90)
    assert(ylim[1] == 90)
