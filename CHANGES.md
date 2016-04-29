0.3 (unreleased)
----------------

- Make sure an error is raised if data is not 3-dimensional and shape doesn’t
  agree with existing data in volume viewer.

- Fix a bug that caused exceptions when clearing/removing layer artists. [#117]

- Workaround OpenGL issue that caused cubes with size > 2048 along any
  dimension to not display.

- Fix issue with _update_data on base VisPy viewer.

- Optimize the layout of options for the layer style editors to save space.

- Added the ability to save static images of the 3D viewers. [#125]

0.2 (2015-03-11)
----------------

- Significant work has gone into making the scatter and volume viewers
  functional. Subsets can be highlighted in either viewer.

0.1 (2015-10-19)
----------------

- Initial release, includes simple volume viewer.
