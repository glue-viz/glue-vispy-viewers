import numpy as np

from glue.core import Data
from glue.core.subset import SubsetState
from glue.core.exceptions import IncompatibleAttribute

from glue.viewers.common3d.compat import update_3d_viewer_state

# For backwards compatibility
update_viewer_state = update_3d_viewer_state


class MultiMaskSubsetState(SubsetState):
    """
    A subset state that can include a different mask for different datasets.

    This is useful when doing 3D selections with multiple datasets. This used
    to be a class called MultiElementSubsetState but it is more efficient to
    store masks than element lists. However, for backward-compatibility,
    values of the mask_dict dictionary can be index lists (recognzied because
    they don't have a boolean type).
    """

    def __init__(self, mask_dict=None):
        super(MultiMaskSubsetState, self).__init__()
        mask_dict_uuid = {}
        for key in mask_dict:
            if isinstance(key, Data):
                mask_dict_uuid[key.uuid] = mask_dict[key]
            else:
                mask_dict_uuid[key] = mask_dict[key]
        self._mask_dict = mask_dict_uuid

    def to_mask(self, data, view=None):
        if data.uuid in self._mask_dict:
            mask = self._mask_dict[data.uuid]
            if mask.dtype.kind != 'b':  # backward-compatibility with indices_dict
                indices = mask
                mask = np.zeros(data.shape, dtype=bool)
                mask.flat[indices] = True
            if view is not None:
                mask = mask[view]
            return mask
        else:
            raise IncompatibleAttribute()

    def copy(self):
        state = MultiMaskSubsetState(mask_dict=self._mask_dict)
        return state

    def __gluestate__(self, context):
        serialized = {key: context.do(value) for key, value in self._mask_dict.items()}
        return {'mask_dict': serialized}

    @classmethod
    def __setgluestate__(cls, rec, context):
        # For backward-compatibility reasons we recognize indices_dict
        if 'indices_dict' in rec:
            mask_dict = {key: context.object(value) for key, value in rec['indices_dict'].items()}
        else:
            mask_dict = {key: context.object(value) for key, value in rec['mask_dict'].items()}
        state = cls(mask_dict=mask_dict)
        return state
