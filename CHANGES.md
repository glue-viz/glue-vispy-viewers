0.3 (unreleased)
----------------
- Add back the fov=60. [#124]

- Make sure an error is raised if data is not 3-dimensional and shape doesn’t
  agree with existing data in volume viewer. [#112]

- Raise an explicit error if PyOpenGL is not installed. [#129]

- Fix a bug that caused exceptions when clearing/removing layer artists. [#117]

- Workaround OpenGL issue that caused cubes with size > 2048 along any
  dimension to not display. [#100]

- Fix issue with _update_data on base VisPy viewer. [#106]

- Optimize the layout of options for the layer style editors to save space. [#120]

- Added the ability to save static images of the 3D viewers. [#125]

- Implemented 3D selection. [#103]

- Make sure the 3D viewer is updated if the zorder is set manually. [#132]

- Add selection toolbar and icons for 3D viewers. [#88] [#92] 

0.2 (2015-03-11)
----------------

- Significant work has gone into making the scatter and volume viewers
  functional. Subsets can be highlighted in either viewer.

0.1 (2015-10-19)
----------------

- Initial release, includes simple volume viewer.
