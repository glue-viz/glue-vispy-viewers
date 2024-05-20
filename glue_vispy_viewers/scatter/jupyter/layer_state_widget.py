from ipywidgets import Checkbox, VBox


from glue_jupyter.link import link



class Scatter3DLayerStateWidget(VBox):

    def __init__(self, layer_state):

        self.state = layer_state

        self.widget_visible = Checkbox(description='visible', value=self.state.visible)
        link((self.state, 'visible'), (self.widget_visible, 'value'))

        # self.widget_size = Size(state=self.state)
        # self.widget_color = Color(state=self.state)

        self.widget_vector = Checkbox(description='show vectors', value=self.state.vector_visible)

        # self.widget_vector_x = LinkedDropdown(self.state, 'vx_att', label='vx')
        # self.widget_vector_y = LinkedDropdown(self.state, 'vy_att', label='vy')
        # self.widget_vector_z = LinkedDropdown(self.state, 'vz_att', label='vz')

        # link((self.state, 'vector_visible'), (self.widget_vector, 'value'))
        # dlink((self.widget_vector, 'value'), (self.widget_vector_x.layout, 'display'),
        #       lambda value: None if value else 'none')
        # dlink((self.widget_vector, 'value'), (self.widget_vector_y.layout, 'display'),
        #       lambda value: None if value else 'none')
        # dlink((self.widget_vector, 'value'), (self.widget_vector_z.layout, 'display'),
        #       lambda value: None if value else 'none')

        # link((self.state, 'vector_visible'), (self.widget_vector, 'value'))

        super().__init__([self.widget_visible])
