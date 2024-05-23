import sys
import pytest
from vispy import scene
from ..axes import AxesVisual3D

IS_WIN = sys.platform == 'win32'
PY_LT_39 = sys.version_info[:2] < (3, 9)


@pytest.mark.skipif('PY_LT_39 and IS_WIN', reason="glBindFramebuffer has no attribute '_native'")
def test_3d_axis_visual():

    canvas = scene.SceneCanvas(keys=None, size=(800, 600), show=True)
    view = canvas.central_widget.add_view()
    scene_transform = scene.STTransform()
    view.camera = scene.cameras.TurntableCamera(parent=view.scene,
                                                fov=0., distance=4.0)
    AxesVisual3D(view=view, axis_color='red', transform=scene_transform)

    if hasattr(canvas.native, 'show'):  # Qt
        canvas.native.show()
        canvas.native.close()
