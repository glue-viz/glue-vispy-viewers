# Full changelog

## v1.2.1 - 2024-05-28

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

* Fix validation checks for build distributions by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/386

**Full Changelog**: https://github.com/glue-viz/glue-vispy-viewers/compare/v1.2.0...v1.2.1

## v1.2.0 - 2024-05-24

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### New Features

* Refactor viewer classes to split out Qt from non-Qt part, and define Jupyter viewers by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/381

#### Bug Fixes

* Fixes following Qt/Jupyter split by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/383
* Fix save/record tools in Qt and volume selection tools in Jupyter by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/384
* Fix tests by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/385

#### Other Changes

* Remove isosurface sub-module as it has been broken for a long time by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/382

**Full Changelog**: https://github.com/glue-viz/glue-vispy-viewers/compare/v1.1.0...v1.2.0

## v1.1.0 - 2023-08-21

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

- Updated imports to glue_qt by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/378

**Full Changelog**: https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.7...v1.1.0

## v1.0.7 - 2023-02-11

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Allow axis color to be changed during runtime. by @Carifio24 in https://github.com/glue-viz/glue-vispy-viewers/pull/372
- Drop Python 3.7 and fix compatibility with latest glue-core versions by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/377

### New Contributors

- @Carifio24 made their first contribution in https://github.com/glue-viz/glue-vispy-viewers/pull/372

**Full Changelog**: https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.6...v1.0.7

## v1.0.6 - 2023-01-12

<!-- Release notes generated using configuration in .github/release.yml at main -->
### What's Changed

#### Bug Fixes

- Update API to support `echo>=0.6` and `vispy=0.11` by @dhomeier in https://github.com/glue-viz/glue-vispy-viewers/pull/373
- Fix compatibility with PyQt6 and fix volume rendering with VisPy 0.11+ by @astrofrog in https://github.com/glue-viz/glue-vispy-viewers/pull/376

#### Other Changes

- Switch CI to GitHub actions by @dhomeier in https://github.com/glue-viz/glue-vispy-viewers/pull/371

### New Contributors

- @dhomeier made their first contribution in https://github.com/glue-viz/glue-vispy-viewers/pull/371

**Full Changelog**: https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.5...v1.0.6

## [1.0.5](https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.4...v1.0.5) - 2021-10-28

### What's Changed

#### Bug Fixes

- Include vispy vertex shader to fix compatibility with vispy v0.9.1 and later. [https://github.com/glue-viz/glue-vispy-viewers/pull/370]

## [1.0.4](https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.3...v1.0.4) - 2021-10-17

#### Bug Fixes

- Fix compatibility with vispy v0.9.0. [https://github.com/glue-viz/glue-vispy-viewers/pull/369]

## [1.0.3](https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.2...v1.0.3) - 2021-07-27

#### Bug Fixes

- Fix deprecation warnings related to echo with recent versions
- of glue-core. [https://github.com/glue-viz/glue-vispy-viewers/pull/367]

## [1.0.2](https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.1...v1.0.2) - 2020-11-24

#### Bug Fixes

- Fix compatibility with latest developer version of vispy. [https://github.com/glue-viz/glue-vispy-viewers/pull/363]

## [1.0.1](https://github.com/glue-viz/glue-vispy-viewers/compare/v1.0.0...v1.0.1) - 2020-10-02

#### Bug Fixes

- Fix 'flip limits' button in 3D scatter plot. [https://github.com/glue-viz/glue-vispy-viewers/pull/361]
- 
- Fix the visual appearance of vectors. [https://github.com/glue-viz/glue-vispy-viewers/pull/362]
- 

## [1.0.0](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.12.1...v1.0.0) - 2020-09-17

### What's Changed

#### New Features

- Add initial support for vectors and error bars.
- [https://github.com/glue-viz/glue-vispy-viewers/pull/358]

#### Other Changes

- Drop support for Python < 3.6. [https://github.com/glue-viz/glue-vispy-viewers/pull/351, https://github.com/glue-viz/glue-vispy-viewers/pull/353]
- 
- No longer bundle vispy, and instead depend on the
- latest stable release. [https://github.com/glue-viz/glue-vispy-viewers/pull/351]
- 

## [0.12.2](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.12.1...v0.12.2) - 2019-06-24

#### Bug Fixes

- Fixed **version** variable which was set to 'undefined'. [https://github.com/glue-viz/glue-vispy-viewers/pull/344]
- 
- Fixed configuration for tox testing tool. [https://github.com/glue-viz/glue-vispy-viewers/pull/344]
- 

## [0.12.1](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.12...v0.12.1) - 2019-06-23

#### Bug Fixes

- Fixed missing package data.

## [0.12](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.11...v0.12) - 2019-06-23

### What's Changed

#### New Features

- Make it possible to view datasets that are linked but not on the same
- pixel grid together. Now also requires datasets to always be linked
- in order to be shown in the same viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/335, https://github.com/glue-viz/glue-vispy-viewers/pull/337]

#### Bug Fixes

- Fix compatibility with the latest developer version of glue. [https://github.com/glue-viz/glue-vispy-viewers/pull/339, https://github.com/glue-viz/glue-vispy-viewers/pull/342]
- 
- Fix bug with hidden layers in the 3D scatter viewer becoming visible after
- saving and loading session file. [https://github.com/glue-viz/glue-vispy-viewers/pull/340]
- 

## [0.11](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.10...v0.11) - 2018-11-14

### What's Changed

#### New Features

- Make it so that selection tools are de-selected after use, to be
- consistent with the core glue behavior. [https://github.com/glue-viz/glue-vispy-viewers/pull/320]
- 
- Implement the 'data' and 'outline' modes for volume rendering of subsets
- directly in the OpenGL shader. [https://github.com/glue-viz/glue-vispy-viewers/pull/310]
- 
- Make volume rendering be adaptive in terms of resolution - the buffer used
- for the rendering is a fixed size and the data in the buffer is updated as
- the user zooms in/out and pans around. [https://github.com/glue-viz/glue-vispy-viewers/pull/312]
- 

#### Bug Fixes

- Fixed the home button in the toolbar to reset limits in addition to the
- viewing angle. [https://github.com/glue-viz/glue-vispy-viewers/pull/327]
- 
- Fix a bug that caused crashes when not all scatter points were inside the
- 3D scatter viewer box (due e.g. to panning and/or zooming) and color-coding
- of points was used. [https://github.com/glue-viz/glue-vispy-viewers/pull/326]
- 
- Fix a bug that caused an error when adding a dataset with an incompatible
- subset to a new 3D scatter viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/323]
- 
- Improve how we deal with reaching the limit of the number of free slots
- in the volume viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/321]
- 
- Fixed a bug that caused layers to sometimes non-deterministically be
- shown/hidden and/or not disappear correctly. [https://github.com/glue-viz/glue-vispy-viewers/pull/314]
- 

## [0.10](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.9.2...v0.10) - 2018-04-27

### What's Changed

#### New Features

- Use new 3D and flood fill subset state classes from glue to make storing
- subsets much more efficient. [https://github.com/glue-viz/glue-vispy-viewers/pull/301]
- 
- Improve performance for volume rendering for arrays larger than 2048
- along one or more dimensions. [https://github.com/glue-viz/glue-vispy-viewers/pull/303]
- 
- Improve performance when closing a session that has large volume
- visualizations. [https://github.com/glue-viz/glue-vispy-viewers/pull/307]
- 
- Improve performance when clipping the data outside the box. [https://github.com/glue-viz/glue-vispy-viewers/pull/307]
- 

#### Bug Fixes

- Work around an issue on certain graphics cards which causes volume
- renderings to not appear correctly but instead of have stripe artifacts. [https://github.com/glue-viz/glue-vispy-viewers/pull/303]
- 
- Fixed a bug that caused layers to be shown/hidden out of sync with
- checkboxes. [https://github.com/glue-viz/glue-vispy-viewers/pull/307]
- 
- Fixed a bug that caused circular references to viewers to cause issues
- after the viewers were closed. [https://github.com/glue-viz/glue-vispy-viewers/pull/307]
- 

## [0.9.2](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.9.1...v0.9.2) - 2018-03-08

#### Bug Fixes

- Fix bug that caused a crash when adding a volume to a viewer that
- already had a viewer and scatter layer. [https://github.com/glue-viz/glue-vispy-viewers/pull/291]

## [0.9.1](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.9...v0.9.1) - 2018-01-09

#### Bug Fixes

- Fix compatibility of 3D viewers with PyQt5 on Linux. [https://github.com/glue-viz/glue-vispy-viewers/pull/287]

## [0.9](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.8...v0.9) - 2017-10-25

### What's Changed

#### New Features

- Improve performance for volume rendering. [https://github.com/glue-viz/glue-vispy-viewers/pull/274]

#### Bug Fixes

- Fix layer artist icon when using colormaps. [https://github.com/glue-viz/glue-vispy-viewers/pull/283]
- 
- Fix bug that occurred when downsampling cubes with more than 2048 elements
- in one or more dimensions. [https://github.com/glue-viz/glue-vispy-viewers/pull/277]
- 

## [0.8](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.7.2...v0.8) - 2017-08-22

### What's Changed

#### New Features

- Update viewer code to use non-Qt-specific combo helpers. [https://github.com/glue-viz/glue-vispy-viewers/pull/266]
- 
- Added a home button that resets the view. [https://github.com/glue-viz/glue-vispy-viewers/pull/254]
- 

#### Bug Fixes

- Fix compatibility of floodfill selection with recent Numpy versions. [https://github.com/glue-viz/glue-vispy-viewers/pull/257, https://github.com/glue-viz/glue-vispy-viewers/pull/267]
- 
- Avoid errors when lower and upper limits in viewer options are equal. [https://github.com/glue-viz/glue-vispy-viewers/pull/268]
- 
- Fix bug that caused the color of scatter plots to not always update. [https://github.com/glue-viz/glue-vispy-viewers/pull/265]
- 
- Fix color and size encoding when using the data clip option. [https://github.com/glue-viz/glue-vispy-viewers/pull/261]
- 

## [0.7.2](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.7...v0.7.2) - 2017-03-16

#### Bug Fixes

- Fixed bug that caused session files saved after removing subsets
- to no longer be loadable. [https://github.com/glue-viz/glue-vispy-viewers/pull/253]
- 
- Fixed bug that caused record icon to appear multiple times when
- successively creating 3D viewers. [https://github.com/glue-viz/glue-vispy-viewers/pull/252]
- 
- Fixed bug with volume rendering on Windows with Python 2.7, due to
- Numpy .shape returning long integers. [https://github.com/glue-viz/glue-vispy-viewers/pull/245]
- 
- Fixed bug that caused the flipping of size and cmap limits in the
- 3D viewers to not work properly. [https://github.com/glue-viz/glue-vispy-viewers/pull/251]
- 

0.7.1 (unreleased)

#### Bug Fixes

- Fixed bugs with 3D selections following refactoring. [https://github.com/glue-viz/glue-vispy-viewers/pull/243]
- 
- Fixed the case where vmin == vmax for size or color. [https://github.com/glue-viz/glue-vispy-viewers/pull/243]
- 

## [0.7](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.6...v0.7) - 2017-02-15

### What's Changed

#### New Features

- When multiple datasets are visible in a 3D view, selections now apply to
- all of them (except for point and point and drag selections, for which the
- selection applies to the currently selected layer). [https://github.com/glue-viz/glue-vispy-viewers/pull/208]
- 
- Refactored the viewers to simplify the code and make development easier. [https://github.com/glue-viz/glue-vispy-viewers/pull/238]
- 
- Improve the default level selection for the isosurface viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/238]
- 

#### Other Changes

- The selection tools have been refactored to use the new toolbar/tool
- infrastructure in glue. [https://github.com/glue-viz/glue-vispy-viewers/pull/208]
- 
- Update all layers in 3D viewers if numerical values change in any datasaet. [https://github.com/glue-viz/glue-vispy-viewers/pull/236]
- 

## [0.6](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.5...v0.6) - 2016-11-03

#### Bug Fixes

- Fixed a bug that caused subsets to not be added to viewers when adding a
- dataset with already existing subsets. [https://github.com/glue-viz/glue-vispy-viewers/pull/218]
- 
- Fixed compatibility with Qt5. [https://github.com/glue-viz/glue-vispy-viewers/pull/212]
- 
- Fixed a bug that caused session files created previously to not be
- openable. [https://github.com/glue-viz/glue-vispy-viewers/pull/213, https://github.com/glue-viz/glue-vispy-viewers/pull/214]
- 
- Fixed a bug that caused 3D selections to not work properly. [https://github.com/glue-viz/glue-vispy-viewers/pull/219]
- 

## [0.5](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.4...v0.5) - 2016-10-10

### What's Changed

#### New Features

- Watch for `NumericalDataChangedMessage` messages. [https://github.com/glue-viz/glue-vispy-viewers/pull/183, https://github.com/glue-viz/glue-vispy-viewers/pull/184]
- 
- Add support for overplotting scatter markers on top of volumes. [https://github.com/glue-viz/glue-vispy-viewers/pull/200]
- 
- Add support for n-dimensional components in 3D scatter plot viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/158]
- 
- Factor of ~10 improvement in performance when selecting data in the scatter
- or volume viewers. [https://github.com/glue-viz/glue-vispy-viewers/pull/165]
- 
- Make selection frame wider. [https://github.com/glue-viz/glue-vispy-viewers/pull/161]
- 
- Small fix of the camera initial settings & rotate speed . [https://github.com/glue-viz/glue-vispy-viewers/pull/154]
- 
- Advanced point-mode selection for scatter points. [https://github.com/glue-viz/glue-vispy-viewers/pull/160]
- 
- Experimental point-mode selection for volume viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/159]
- 
- Add an option to clip any data outside the specified limits. [https://github.com/glue-viz/glue-vispy-viewers/pull/203]
- 
- Add a checkbox to force the aspect ratio to be native instead of
- making all axes the same length. [https://github.com/glue-viz/glue-vispy-viewers/pull/205]
- 

#### Bug Fixes

- Fixed a bug that caused alpha scaling to not work correctly when mapping
- scatter marker colors to an attribute. [https://github.com/glue-viz/glue-vispy-viewers/pull/201]
- 
- Fixed a bug that caused color-coding and size-scaling of points in 3D viewer
- to not work for negative values. [https://github.com/glue-viz/glue-vispy-viewers/pull/182, https://github.com/glue-viz/glue-vispy-viewers/pull/185]
- 
- Fix button to record animations when the user cancels the file save dialog.
- [https://github.com/glue-viz/glue-vispy-viewers/pull/186]
- 
- Fix Qt imports to use QtPy for new versions of glue. [https://github.com/glue-viz/glue-vispy-viewers/pull/173, https://github.com/glue-viz/glue-vispy-viewers/pull/178, https://github.com/glue-viz/glue-vispy-viewers/pull/186]
- 

## [0.4](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.3...v0.4) - 2016-05-24

- Add a checkbox to toggle between near and far-field view. [https://github.com/glue-viz/glue-vispy-viewers/pull/140]
- 
- Support the options in Glue v0.8 for foreground and background colors in viewers. [https://github.com/glue-viz/glue-vispy-viewers/pull/149]
- 

#### Bug Fixes

- Fix a bug that caused subsets selected in the 3D viewers to be applied to
- datasets for which they aren't relevant. [https://github.com/glue-viz/glue-vispy-viewers/pull/151]

#### Other Changes

- Bundle the latest developer version of VisPy. [https://github.com/glue-viz/glue-vispy-viewers/pull/143, https://github.com/glue-viz/glue-vispy-viewers/pull/144]

## [0.3](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.2...v0.3) - 2016-05-04

### What's Changed

#### New Features

- Add selection toolbar and icons for 3D viewers. [https://github.com/glue-viz/glue-vispy-viewers/pull/88, https://github.com/glue-viz/glue-vispy-viewers/pull/92]
- 
- Implemented 3D selection. [https://github.com/glue-viz/glue-vispy-viewers/pull/103]
- 
- Optimize the layout of options for the layer style editors to save space. [https://github.com/glue-viz/glue-vispy-viewers/pull/120]
- 
- Added the ability to save static images of the 3D viewers. [https://github.com/glue-viz/glue-vispy-viewers/pull/125]
- 
- Add toolbar icon to continuously rotate the view. [https://github.com/glue-viz/glue-vispy-viewers/pull/128][https://github.com/glue-viz/glue-vispy-viewers/pull/137]
- 
- Implement support for saving 3D viewers in session files. [https://github.com/glue-viz/glue-vispy-viewers/pull/130]
- 
- Added `BACKGROUND_COLOR` and `FOREGROUND_COLOR` settings at root of package. [https://github.com/glue-viz/glue-vispy-viewers/pull/134]
- 
- Save animation with imageio. [https://github.com/glue-viz/glue-vispy-viewers/pull/139]
- 

#### Bug Fixes

- Workaround OpenGL issue that caused cubes with size > 2048 along any
- dimension to not display. [https://github.com/glue-viz/glue-vispy-viewers/pull/100]
- 
- Fix issue with `_update_data` on base VisPy viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/106]
- 
- Make sure an error is raised if data is not 3-dimensional and shape doesn’t
- agree with existing data in volume viewer. [https://github.com/glue-viz/glue-vispy-viewers/pull/112]
- 
- Fix a bug that caused exceptions when clearing/removing layer artists. [https://github.com/glue-viz/glue-vispy-viewers/pull/117]
- 
- Raise an explicit error if PyOpenGL is not installed. [https://github.com/glue-viz/glue-vispy-viewers/pull/129]
- 
- Fix bug that caused all layers in the 3D scatter viewer to disappear when
- one layer was removed. [https://github.com/glue-viz/glue-vispy-viewers/pull/131]
- 
- Make sure the 3D viewer is updated if the zorder is set manually. [https://github.com/glue-viz/glue-vispy-viewers/pull/132]
- 
- Make sure combo boxes don't expand if component names are long. [https://github.com/glue-viz/glue-vispy-viewers/pull/135]
- 

#### Other Changes

- Travis: add back testing against stable glue [https://github.com/glue-viz/glue-vispy-viewers/pull/136]
- 
- Add toggle for perspective view. [https://github.com/glue-viz/glue-vispy-viewers/pull/140]
- 
- Bundle latest developer version of Vispy. [https://github.com/glue-viz/glue-vispy-viewers/pull/143] [https://github.com/glue-viz/glue-vispy-viewers/pull/144]
- 

## [0.2](https://github.com/glue-viz/glue-vispy-viewers/compare/v0.1...v0.2) - 2015-03-11

### What's Changed

#### New Features

- Significant work has gone into making the scatter and volume viewers
- functional. Subsets can be highlighted in either viewer.

## [0.1](https://github.com/glue-vispy-viewers/glue/releases/tag/v0.1) - 2015-10-19

- Initial release, includes simple volume viewer.
