<template>
    <div class="glue-viewer-scatter-3d">
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
            <v-switch v-model="glue_state.visible_axes" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">native aspect ratio</v-subheader>
            <v-switch v-model="glue_state.native_aspect" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">perspective view</v-subheader>
            <v-switch v-model="glue_state.perspective_view" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">clip data</v-subheader>
            <v-switch v-model="glue_state.clip_data" hide-details style="margin-top: 0"/>
        </div>
    </div>
</template>

<style id="viewer_image">
    .glue-viewer-scatter-3d .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
        margin-top: 6px;
    }
</style>
