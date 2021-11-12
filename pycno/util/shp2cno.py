__all__ = ['shp2cno']


def addcnoshape(outf, points, last=False, ctype='cno'):
    """
    Arguments
    ---------
    outf : file-like
        outf is a file that should be in text for cno and binary mode for cnob
    points : list
        list of coordinates [(lon_i, lat_i) for each coordinate pair]
    last : bool
        If last, do not end with 9999 or 999999
    ctype : str
        Choices 'cno' or 'cnob'

    Return
    ------
    None
    """
    import numpy as np

    if ctype not in ('cno', 'cnob'):
        raise TypeError('only currently supporting cno or cnob')

    for lon, lat in points:
        if ctype == 'cno':
            outf.write(f'{lon},{lat}\n')
        elif ctype == 'cnob':
            tmp = (np.array([lon, lat]) * 1000).round(0).astype('>i')
            tmp.tofile(outf)

    if not last:
        if ctype == 'cno':
            outf.write('9999\n')
        elif ctype == 'cnob':
            np.array([999999], dtype='>i').tofile(outf)


def shp2cno(shppath, cnopath):
    """
    Arguments
    ---------
    shppath : str
        Path to shapefile, which should have data in latitude/longitude. If
        data is in another projection, then subsequent plotting will not work.
    cnopath: str
        Path for output. Destination will not be overwritten. Remove to remake.

    Returns
    -------
    None
    """
    import shapefile
    import os

    if os.path.exists(cnopath):
        raise IOError(f'{cnopath} exists; remove to remake')

    ctype = cnopath.split('.')[-1]
    # read in shape path
    shpr = shapefile.Reader(shppath)
    ilastshape = shpr.numRecords - 1

    # Open output file
    if ctype == 'cnob':
        # cnob output must be opened as binary and start with
        # GISSCNOB integer.
        outf = open(cnopath, 'wb')
        outf.write(b'GISSCNOB')
    else:
        # cno files out text files with no header
        outf = open(cnopath, 'w')

    # For each shape, write out its parts.
    # In between parts, write 9999 (cno) or 999999 (cnob)
    for si, shape in enumerate(shpr.iterShapes()):
        if shape.shapeType != shapefile.POLYGON:
            print('**Unexpected shape type:', shape.shapeType)
            print('**Trying anyway')

        # Polygons have at least one part
        starts = [s for s in shape.parts]
        ends = starts[1:] + [len(shape.points)]
        ilastpart = len(starts) - 1
        for pi, (starti, endi) in enumerate(zip(starts, ends)):
            islast = (ilastpart == pi and ilastshape == si)
            addcnoshape(
                outf, shape.points[starti:endi],
                last=islast, ctype=ctype
            )


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--testfig', action='store_true', default=False)
    parser.add_argument('shppath')
    parser.add_argument('cnopath')
    args = parser.parse_args()
    shp2cno(args.shppath, args.cnopath)
    if args.testfig:
        import pycno

        cno = pycno.cno(xlim=(-180, 180), ylim=(-90, 90))
        linec = cno.draw(args.cnopath)
        linec.axes.figure.savefig(args.cnopath + '.png')
