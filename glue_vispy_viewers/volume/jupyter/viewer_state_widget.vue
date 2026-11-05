<template>
    <div class="glue-viewer-volume-3d">
        <div>
            <v-select label="reference" :items="reference_data_items" v-model="reference_data_selected" hide-details />
        </div>
        <div>
            <v-select label="x axis" :items="x_att_items" v-model="x_att_selected" hide-details />
        </div>
        <div>
            <v-select label="y axis" :items="y_att_items" v-model="y_att_selected" hide-details />
        </div>
        <div>
            <v-select label="z axis" :items="z_att_items" v-model="z_att_selected" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">show axes</v-subheader>
            <v-switch v-model="visible_axes" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">native aspect ratio</v-subheader>
            <v-switch v-model="native_aspect" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">perspective view</v-subheader>
            <v-switch v-model="perspective_view" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">clip data</v-subheader>
            <v-switch v-model="clip_data" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-select label="resolution" :items="resolution_items" v-model="resolution_selected" hide-details />
        </div>
        <div>
            <jupyter-widget :widget="widget_slices" />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">cutting plane</v-subheader>
            <v-switch v-model="cut_enabled" hide-details style="margin-top: 0" />
        </div>
        <template v-if="cut_enabled">
            <div>
                <v-select label="mode" :items="cut_mode_items" v-model="cut_mode_selected" hide-details />
            </div>
            <template v-if="(cut_mode_items[cut_mode_selected] || {}).text === 'Simple'">
                <div>
                    <v-subheader class="pl-0 slider-label">axis</v-subheader>
                    <v-btn-toggle :value="cut_axis_selected" @change="cut_axis_selected = $event" mandatory dense>
                        <v-btn v-for="(item, idx) in cut_axis_items" :key="item.text" :value="idx" small>{{ item.text }}</v-btn>
                    </v-btn-toggle>
                </div>
            </template>
            <template v-else>
                <div>
                    <v-subheader class="pl-0 slider-label">tilt</v-subheader>
                    <v-slider v-model="cut_tilt" :min="0" :max="3.14159" :step="0.01" hide-details thumb-label="hidden" />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">rotation</v-subheader>
                    <v-slider v-model="cut_rotation" :min="0" :max="6.28318" :step="0.01" hide-details thumb-label="hidden" />
                </div>
            </template>
            <div>
                <v-subheader class="pl-0 slider-label">depth</v-subheader>
                <v-slider v-model="cut_depth" :min="0" :max="1" :step="0.001" hide-details thumb-label="hidden" />
            </div>
            <div>
                <v-subheader class="pl-0 slider-label">plane image opacity</v-subheader>
                <v-slider v-model="cut_plane_image_opacity" :min="0" :max="1" :step="0.001" hide-details thumb-label="hidden" />
            </div>
            <div>
                <v-subheader class="pl-0 slider-label">plane background</v-subheader>
                <v-menu ref="menu">
                    <template v-slot:activator="{ on, props }">
                        <span class="glue-color-menu"
                              @click.stop="on.click"
                        >&nbsp;</span>
                    </template>
                    <div @click.stop="" style="text-align: end; background-color: white">
                        <v-btn icon @click="$refs.menu.save()">
                            <v-icon>mdi-close</v-icon>
                        </v-btn>
                        <v-color-picker v-model="cut_plane_image_bgcolor" echo-type="text" ></v-color-picker>
                    </div>
                </v-menu>
            </div>
            <div>
                <v-btn small block class="mt-2" @click="flip_cut">Flip shown/clipped side</v-btn>
            </div>
        </template>
    </div>
</template>

<style id="viewer_image">
    .glue-viewer-volume-3d .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
        margin-top: 6px;
    }
</style>
