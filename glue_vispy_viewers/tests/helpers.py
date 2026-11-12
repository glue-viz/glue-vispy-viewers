from functools import wraps
from io import BytesIO

import pytest


# Compat shim for ``glue.core.fixed_resolution_buffer.invalidate_cache`` which
# was added after the most recent glue-core release. Once a release ships with
# the upstream function, drop this block and import it directly.
try:
    from glue.core.fixed_resolution_buffer import invalidate_cache
except ImportError:
    from glue.core.fixed_resolution_buffer import PIXEL_CACHE, ARRAY_CACHE

    def invalidate_cache(data=None):
        # We only ever call this with no argument from the visual-test
        # decorators, so the per-data-object path is not implemented here.
        PIXEL_CACHE.clear()
        ARRAY_CACHE.clear()

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
        @pytest.mark.mpl_image_compare(tolerance=tolerance, deterministic=True, **kwargs)
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
    # Initial settle wait before we start polling for the first frame.
    settle_ms = kwargs.pop("settle_ms", 1000)
    # Maximum extra time to spend waiting for jupyter_rfb to stream the
    # first non-grey frame. Volume rendering (256^3 texture ray-march) is
    # noticeably slower than scatter, and CI is slower than a laptop.
    max_wait_ms = kwargs.pop("max_wait_ms", 15000)
    # After the heuristic first says the frame has arrived, keep polling
    # until two consecutive screenshots are byte-identical (the canvas
    # has stopped repainting), or this hard cap elapses. Catches the case
    # where the render passes the "not grey anymore" check while still
    # mid-stream and the screenshot captures a partial paint.
    stable_wait_ms = kwargs.pop("stable_wait_ms", 5000)
    stable_poll_ms = kwargs.pop("stable_poll_ms", 250)

    def decorator(test_function):

        @pytest.mark.mpl_image_compare(tolerance=tolerance, deterministic=True, **kwargs)
        @wraps(test_function)
        def wrapper(tmp_path, page_session, *a, **kw):
            import time
            from IPython.display import display
            layout = test_function(tmp_path, page_session, *a, **kw)
            layout.add_class("test-viewer")
            display(layout)
            locator = page_session.locator(".test-viewer")
            locator.wait_for()
            page_session.wait_for_timeout(settle_ms)

            # Poll until the canvas has streamed a real frame rather than
            # the jupyter_rfb "first frame pending" placeholder (a uniform
            # grey (127, 127, 127) fill). A real render has lots of colour
            # variation; the placeholder is near-uniform.
            #
            # The check must inspect only the *interior* of the screenshot:
            # the wrapping widget always contributes a handful of non-grey
            # chrome/border pixels, so a variance check over the full image
            # is satisfied on the very first poll -- the loop would exit
            # before the canvas has actually painted and capture the grey
            # placeholder. Cropping away the chrome makes the check reflect
            # the canvas content alone, so the loop genuinely waits for the
            # streamed frame. This matters on a cold/slow CI runner, where
            # the first frame can arrive later than ``settle_ms``.
            #
            # Falls through after max_wait_ms even if still grey, so a
            # broken pipeline still produces a comparable image.
            def _frame_rendered(png_bytes):
                rgb = Image.open(BytesIO(png_bytes)).convert('RGB')
                width, height = rgb.size
                interior = rgb.crop((width // 4, height // 4,
                                     3 * width // 4, 3 * height // 4))
                low, high = interior.getextrema()[0]
                return high - low > 20

            start = time.monotonic()
            screenshot = locator.screenshot()
            while (not _frame_rendered(screenshot)
                   and (time.monotonic() - start) * 1000 < max_wait_ms):
                page_session.wait_for_timeout(500)
                screenshot = locator.screenshot()

            # The "non-grey" heuristic only catches the transition out of
            # the placeholder -- the canvas can still be mid-paint when it
            # passes (e.g. axis labels arrive a few frames after the data
            # markers). Re-screenshot until two successive captures are
            # byte-identical, meaning the canvas has stopped updating.
            # Capped so a continuously-animating canvas can't hang the
            # test forever.
            stable_start = time.monotonic()
            previous = screenshot
            page_session.wait_for_timeout(stable_poll_ms)
            screenshot = locator.screenshot()
            while (screenshot != previous
                   and (time.monotonic() - stable_start) * 1000 < stable_wait_ms):
                previous = screenshot
                page_session.wait_for_timeout(stable_poll_ms)
                screenshot = locator.screenshot()

            # The test returns a widget, not the viewer, so we can't close
            # the viewer here. Invalidate the glue caches so the conftest
            # teardown check is satisfied; the viewer is GC'd shortly after.
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
        @pytest.mark.mpl_image_compare(tolerance=tolerance, deterministic=True, **kwargs)
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
            invalidate_cache()
            return _PngFigure(buf.getvalue())

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])

    return decorator


def visual_test_export(*args, **kwargs):
    """
    Decorator for functions that test the export of an image file.

    The wrapped function should return the filepath of the saved image.
    The decorator opens the filepath and passes its bytes to `pytest-mpl`
    using the same figure-shaped wrapper as `visual_test`.
    """

    tolerance = kwargs.pop('tolerance', 0)

    def decorator(test_function):

        @pytest.mark.skipif(not HAS_VISUAL_TEST_DEPS,
                            reason="requires pytest-mpl, Pillow")
        @pytest.mark.mpl_image_compare(tolerance=tolerance, deterministic=True, **kwargs)
        @wraps(test_function)
        def wrapper(*a, **kw):
            path = test_function(*a, **kw)
            image = Image.open(path)
            buf = BytesIO()
            image.save(buf, format='PNG')
            return _PngFigure(buf.getvalue())

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])

    return decorator
