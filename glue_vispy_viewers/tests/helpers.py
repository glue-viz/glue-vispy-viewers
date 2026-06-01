from functools import wraps
from io import BytesIO

import pytest

try:
    import vispy
    # Select an offscreen-capable backend so canvas.render() returns real
    # pixels. On Linux this still needs an X server (use Xvfb in CI); the
    # jupyter_rfb backend returns a 1x1 dummy when not displayed in a notebook
    # and is therefore unsuitable for headless rendering.
    vispy.use(app='glfw')
    import pytest_mpl  # noqa: F401
    from PIL import Image
except ImportError:
    HAS_VISUAL_TEST_DEPS = False
else:
    HAS_VISUAL_TEST_DEPS = True


__all__ = ['HAS_VISUAL_TEST_DEPS', 'visual_test', 'set_canvas_size']


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
            return _PngFigure(buf.getvalue())

        return wrapper

    if len(args) == 1 and callable(args[0]):
        return decorator(args[0])

    return decorator
