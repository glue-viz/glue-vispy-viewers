import numpy as np

from vispy.visuals.transforms import (ChainTransform, NullTransform,
                                      MatrixTransform, STTransform)
from vispy.visuals.transforms.base_transform import InverseTransform
from vispy.visuals.transforms._util import arg_to_vec4


def as_matrix_transform(transform):
    """
    Simplify a transform to a single matrix transform, which makes it a lot
    faster to compute transformations.

    Raises a TypeError if the transform cannot be simplified.
    """
    if isinstance(transform, ChainTransform):
        matrix = np.identity(4)
        for tr in transform.transforms:
            # We need to do the matrix multiplication manually because VisPy
            # somehow doesn't mutliply matrices if there is a perspective
            # component. The equation below looks like it's the wrong way
            # around, but the VisPy matrices are transposed.
            matrix = np.matmul(as_matrix_transform(tr).matrix, matrix)
        return MatrixTransform(matrix)
    elif isinstance(transform, InverseTransform):
        matrix = as_matrix_transform(transform._inverse)
        return MatrixTransform(matrix.inv_matrix)
    elif isinstance(transform, NullTransform):
        return MatrixTransform()
    elif isinstance(transform, STTransform):
        return transform.as_matrix()
    elif isinstance(transform, MatrixTransform):
        return transform
    else:
        raise TypeError("Could not simplify transform of type {0}".format(type(transform)))


class NestedSTTransform(STTransform):

    glsl_map = """
        vec4 st_transform_map(vec4 pos) {
            return vec4((pos.xyz * $innerscale.xyz + $innertranslate.xyz * pos.w).xyz
                         * $scale.xyz + $translate.xyz * pos.w, pos.w);
        }
    """

    glsl_imap = """
        vec4 st_transform_imap(vec4 pos) {
            return vec4((((pos.xyz - $innertranslate.xyz * pos.w) / $innerscale.xyz)
                         - $translate.xyz * pos.w) / $scale.xyz, pos.w);
        }
    """

    def __init__(self):
        self.inner = STTransform()
        super(NestedSTTransform, self).__init__()

    @arg_to_vec4
    def map(self, coords):
        coords = self.inner.map(coords)
        coords = super(NestedSTTransform, self).map(coords)
        return coords

    @arg_to_vec4
    def imap(self, coords):
        coords = super(NestedSTTransform, self).imap(coords)
        coords = self.inner.imap(coords)
        return coords

    def _update_shaders(self):
        self._shader_map['scale'] = self.scale
        self._shader_map['translate'] = self.translate
        self._shader_imap['scale'] = self.scale
        self._shader_imap['translate'] = self.translate
        self._shader_map['innerscale'] = self.inner.scale
        self._shader_map['innertranslate'] = self.inner.translate
        self._shader_imap['innerscale'] = self.inner.scale
        self._shader_imap['innertranslate'] = self.inner.translate
