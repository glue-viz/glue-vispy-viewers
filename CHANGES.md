0.8 (unreleased)
----------------

- No changes yet.

0.7.2 (unreleased)
------------------

- Fixed bug with volume rendering on Windows with Python 2.7, due to
  Numpy .shape returning long integers. [#245]

- Fixed bug that caused the flipping of size and cmap limits in the
  3D viewers to not work properly. [#251]

0.7.1 (unreleased)
------------------

- Fixed bugs with 3D selections following refactoring. [#243]

- Fixed the case where vmin == vmax for size or color. [#243]

0.7 (2017-02-15)
----------------

- When multiple datasets are visible in a 3D view, selections now apply to
  all of them (except for point and point and drag selections, for which the
  selection applies to the currently selected layer). [#208]

- The selection tools have been refactored to use the new toolbar/tool
  infrastructure in glue. [#208]

- Update all layers in 3D viewers if numerical values change in any datasaet. [#236]

- Refactored the viewers to simplify the code and make development easier. [#238]

- Improve the default level selection for the isosurface viewer. [#238]

0.6 (2016-11-03)
----------------

- Fixed a bug that caused subsets to not be added to viewers when adding a
  dataset with already existing subsets. [#218]

- Fixed compatibility with Qt5. [#212]

- Fixed a bug that caused session files created previously to not be
  openable. [#213, #214]

- Fixed a bug that caused 3D selections to not work properly. [#219]

0.5 (2016-10-10)
----------------

- Fixed a bug that caused alpha scaling to not work correctly when mapping
  scatter marker colors to an attribute. [#201]

- Watch for ``NumericalDataChangedMessage`` messages. [#183, #184]

- Fixed a bug that caused color-coding and size-scaling of points in 3D viewer
  to not work for negative values. [#182, #185]

- Add support for overplotting scatter markers on top of volumes. [#200]

- Add support for n-dimensional components in 3D scatter plot viewer. [#158]

- Factor of ~10 improvement in performance when selecting data in the scatter
  or volume viewers. [#165]

- Make selection frame wider. [#161]

- Small fix of the camera initial settings & rotate speed . [#154]

- Advanced point-mode selection for scatter points. [#160]

- Experimental point-mode selection for volume viewer. [#159]

- Fix button to record animations when the user cancels the file save dialog.
  [#186]

- Fix Qt imports to use QtPy for new versions of glue. [#173, #178, #186]

- Add an option to clip any data outside the specified limits. [#203]

- Add a checkbox to force the aspect ratio to be native instead of
  making all axes the same length. [#205]

0.4 (2016-05-24)
----------------

- Bundle the latest developer version of VisPy. [#143, #144]

- Add a checkbox to toggle between near and far-field view. [#140]

- Support the options in Glue v0.8 for foreground and background colors in viewers. [#149]

- Fix a bug that caused subsets selected in the 3D viewers to be applied to
  datasets for which they aren't relevant. [#151]

0.3 (2016-05-04)
----------------

- Add selection toolbar and icons for 3D viewers. [#88, #92]

- Workaround OpenGL issue that caused cubes with size > 2048 along any
  dimension to not display. [#100]

- Implemented 3D selection. [#103]

- Fix issue with _update_data on base VisPy viewer. [#106]

- Make sure an error is raised if data is not 3-dimensional and shape doesn’t
  agree with existing data in volume viewer. [#112]

- Fix a bug that caused exceptions when clearing/removing layer artists. [#117]

- Optimize the layout of options for the layer style editors to save space. [#120]

- Added the ability to save static images of the 3D viewers. [#125]

- Add toolbar icon to continuously rotate the view. [#128][#137]

- Raise an explicit error if PyOpenGL is not installed. [#129]

- Implement support for saving 3D viewers in session files. [#130]

- Fix bug that caused all layers in the 3D scatter viewer to disappear when
  one layer was removed. [#131]

- Make sure the 3D viewer is updated if the zorder is set manually. [#132]

- Added ``BACKGROUND_COLOR`` and ``FOREGROUND_COLOR`` settings at root of package. [#134]

- Make sure combo boxes don't expand if component names are long. [#135]

- Travis: add back testing against stable glue [#136]

- Save animation with imageio. [#139]

- Add toggle for perspective view. [#140]

- Bundle latest developer version of Vispy. [#143] [#144]



0.2 (2015-03-11)
----------------

- Significant work has gone into making the scatter and volume viewers
  functional. Subsets can be highlighted in either viewer.

0.1 (2015-10-19)
----------------

- Initial release, includes simple volume viewer.
