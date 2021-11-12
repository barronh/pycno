0.2
===

0.2.0
-----

* Added shapefile conversion utilities.
* Added tox for client-side continuous integration.
* Improved some documentation.
* Impoved flake8 warning and error compliance.
* The next update will move pycno to version 1.0.0.

0.1
===

0.1.3
-----

* Added this changelog.
* Added cno text file capabilities.
* Added show_version function comparable to pyproj
* Fixed distribution of default cno and cnob files
* Added tests with known simple data, which allows for better checking.
  * testing for unprojected compares to known raw data values
  * testing for projected data uses a known *good* run

0.1.2
-----

* Improved documentation within distributed package.

0.1.1
-----

* Fixed caching features to prevent re-reading and reprojecting for each draw.

0.1.0
-----

Initial version for use by the public. Includes support for:

* reading CNOB files
* projecting lon/lat to pyproj-based projection
* capability to read from a CNOB store location, which can be set
  by environmental variable PYCNO_DATA.
* caching features to prevent re-reading and reprojecting for each draw.
* includes basic documentation

0.0
===

0.0.1
-----

Initial code. Reads CNOB and draws on axes.

to-do
=====

Priority items will be added here.
