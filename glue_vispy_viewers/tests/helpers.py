from functools import wraps
from io import BytesIO

import pytest

try:
    import vispy
    import pytest_mpl  # noqa: F401
    from PIL import Image
except ImportError:
    HAS_VISUAL_TEST_DEPS = False
else:
    HAS_VISUAL_TEST_DEPS = True
    # Select an offscreen-capable backend so canvas.render() returns real
    # pixels. On Linux this still needs an X server (use Xvfb in CI); the
    # jupyter_rfb backend returns a 1x1 dummy when not displayed in a notebook
    # and is therefore unsuitable for headless rendering.
    #
    # vispy.use raises RuntimeError if a backend has already been locked in,
    # even when re-selecting the same backend. The Jupyter canary in
    # particular pre-pins jupyter_rfb before pulling in this module via the
    # visual_test_jupyter decorator, so we tolerate that case here.
    try:
        vispy.use(app='glfw')
    except RuntimeError:
        pass


__all__ = ['HAS_VISUAL_TEST_DEPS', 'visual_test', 'visual_test_qt',
           'visual_test_jupyter', 'set_canvas_size', 'inverted_glue_colors']


import contextlib


@contextlib.contextmanager
def inverted_glue_colors():
    """
    Temporarily swap glue's BACKGROUND_COLOR / FOREGROUND_COLOR settings
    to a dark theme (black background, white axes) for the duration of
    the ``with`` block.

    The vispy widget reads these settings at construction time and uses
    them for ``canvas.bgcolor`` and the axis colours, so the viewer must
    be constructed *inside* the ``with`` block; the canvas then retains
    the inverted colours after the context exits.
    """
    from glue.config import settings
    old_bg = settings.BACKGROUND_COLOR
    old_fg = settings.FOREGROUND_COLOR
    settings.BACKGROUND_COLOR = '#000000'
    settings.FOREGROUND_COLOR = '#FFFFFF'
    try:
        yield
    finally:
        settings.BACKGROUND_COLOR = old_bg
        settings.FOREGROUND_COLOR = old_fg


def set_canvas_size(viewer_or_canvas, width, height):
    """
    Resize a vispy canvas and propagate the change to the camera.

    Setting ``canvas.size`` alone updates only the output buffer; the
    viewbox/camera aspect ratio stays at the construction-time default,
    which clips the scene when the new size has a different aspect. Firing
    ``canvas.events.resize`` mirrors what a real Qt or browser window would
    do when resized, and is what lets the camera refit the view.
    """
    canvas = (viewer_or_canvas._vispy_widget.canvas
              if hasattr(viewer_or_canvas, '_vispy_widget')
              else viewer_or_canvas)
    canvas.size = (width, height)
    canvas.events.resize(size=(width, height))


class _PngFigure:

    def __init__(self, png_bytes):
        self._png_bytes = png_bytes

    def savefig(self, filename_or_fileobj, *args, **kwargs):
        if isinstance(filename_or_fileobj, str):
            with open(filename_or_fileobj, 'wb') as f:
                f.write(self._png_bytes)
        else:
            filename_or_fileobj.write(self._png_bytes)


def visual_test(*args, **kwargs):
    """
    Decorator for visual regression tests of vispy-rendered viewers.

    The test function should return either a glue-vispy-viewers viewer
    instance, a ``vispy.scene.SceneCanvas``, or any object with a ``.canvas``
    attribute that exposes ``render()``. The decorator calls ``render()``,
    encodes the resulting RGBA array as PNG, and hands the bytes to
    ``pytest-mpl`` via a tiny figure-shaped wrapper.
    """

    tolerance = kwargs.pop("tolerance", 0)

    def decorator(test_function):

        @pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS,
                            reason="requires pytest-mpl, Pillow, vispy[glfw]")
        @pytest.mark.mpl_image_compare(tolerance=tolerance, **kwargs)
        @wraps(test_function)
        def wrapper(*a, **kw):
            result = test_function(*a, **kw)
            if hasattr(result, '_vispy_widget'):
                canvas = result._vispy_widget.canvas
            elif hasattr(result, 'canvas'):
                canvas = result.canvas
            else:
                canvas = result
            img = canvas.render()
            buf = BytesIO()
            Image.fromarray(img).save(buf, format='PNG')
            # The repo's conftest enforces glue's PIXEL_CACHE / ARRAY_CACHE
            # are empty in its pytest_runtest_teardown hook, which fires
            # *before* any xunit teardown_method, so we have to close the
            # viewer here in the wrapper to release the caches in time.
            if hasattr(result, 'close'):
                result.close()
            return _PngFigure(buf.getvalue())

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])

    return decorator


def visual_test_jupyter(*args, **kwargs):
    """
    Decorator for Jupyter-host visual canary tests.

    Adapted from ``glue_jupyter.tests.helpers.visual_widget_test``: displays
    the returned widget in a solara test page, screenshots it via Playwright,
    and feeds the bytes to ``pytest-mpl``. The one difference is an explicit
    ``settle_ms`` wait between the locator becoming visible and the
    screenshot — jupyter_rfb does not stream its first frame until after the
    canvas mounts and requests it, so the default
    ``wait_for(state="visible")`` is not enough.
    """

    tolerance = kwargs.pop("tolerance", 0)
    settle_ms = kwargs.pop("settle_ms", 2000)

    def decorator(test_function):

        @pytest.mark.mpl_image_compare(tolerance=tolerance, **kwargs)
        @wraps(test_function)
        def wrapper(tmp_path, page_session, *a, **kw):
            from IPython.display import display
            layout = test_function(tmp_path, page_session, *a, **kw)
            layout.add_class("test-viewer")
            display(layout)
            locator = page_session.locator(".test-viewer")
            locator.wait_for()
            page_session.wait_for_timeout(settle_ms)
            screenshot = locator.screenshot()
            # The test returns a widget, not the viewer, so we can't close
            # the viewer here. Invalidate the glue caches so the conftest
            # teardown check is satisfied; the viewer is GC'd shortly after.
            from glue.core.fixed_resolution_buffer import invalidate_cache
            invalidate_cache()
            return _PngFigure(screenshot)

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])

    return decorator


def visual_test_qt(*args, **kwargs):
    """
    Decorator for Qt-host visual canary tests.

    Same shape as ``visual_test``: the wrapped function returns a Qt
    viewer (or anything with ``_vispy_widget.canvas``). The decorator
    flushes the Qt event loop and captures ``canvas.render()`` from the
    *Qt-backed* vispy context (not GLFW), so it verifies the Qt wrapper
    doesn't corrupt the rendering pipeline.
    """

    tolerance = kwargs.pop("tolerance", 0)

    def decorator(test_function):

        @pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS,
                            reason="requires pytest-mpl, Pillow")
        @pytest.mark.mpl_image_compare(tolerance=tolerance, **kwargs)
        @wraps(test_function)
        def wrapper(*a, **kw):
            from glue_qt.utils import get_qapp
            qapp = get_qapp()
            result = test_function(*a, **kw)
            qapp.processEvents()
            if hasattr(result, '_vispy_widget'):
                canvas = result._vispy_widget.canvas
            elif hasattr(result, 'canvas'):
                canvas = result.canvas
            else:
                canvas = result
            img = canvas.render()
            buf = BytesIO()
            Image.fromarray(img).save(buf, format='PNG')
            # Qt's class-based teardown_method calls viewer.close() and
            # app.close() — but conftest's PIXEL_CACHE check fires first,
            # so we invalidate here. Close still runs cleanly afterwards
            # thanks to the volume_visual.deallocate fix.
            from glue.core.fixed_resolution_buffer import invalidate_cache
            invalidate_cache()
            return _PngFigure(buf.getvalue())

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])

    return decorator
