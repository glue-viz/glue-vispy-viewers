from glue_vispy_viewers.extern.vispy.visuals.transforms import ChainTransform, NullTransform, MatrixTransform, STTransform
from glue_vispy_viewers.extern.vispy.visuals.transforms.base_transform import InverseTransform


def as_matrix_transform(transform):
    """
    Simplify a transform to a single matrix transform, which makes it a lot
    faster to compute transformations.

    Raises a TypeError if the transform cannot be simplified.
    """
    if isinstance(transform, ChainTransform):
        matrix = MatrixTransform()
        for tr in transform.transforms:
            matrix = matrix * as_matrix_transform(tr)
        return matrix
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
