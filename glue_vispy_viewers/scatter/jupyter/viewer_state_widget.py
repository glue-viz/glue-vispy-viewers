from ipywidgets import Checkbox, VBox


from glue_jupyter.link import link
from glue_jupyter.widgets import LinkedDropdown


class Scatter3DViewerStateWidget(VBox):

    def __init__(self, viewer_state):

        self.state = viewer_state

        self.widget_show_axes = Checkbox(value=False, description="Show axes")
        link((self.state, 'visible_axes'), (self.widget_show_axes, 'value'))

        self.widget_native_aspect = Checkbox(value=False, description="Native aspect ratio")
        link((self.state, 'native_aspect'), (self.widget_native_aspect, 'value'))

        self.widgets_axis = []
        for i, axis_name in enumerate('xyz'):
            widget_axis = LinkedDropdown(self.state, axis_name + '_att',
                                         label=axis_name + ' axis')
            self.widgets_axis.append(widget_axis)

        super().__init__([self.widget_show_axes, self.widget_native_aspect] + self.widgets_axis)
