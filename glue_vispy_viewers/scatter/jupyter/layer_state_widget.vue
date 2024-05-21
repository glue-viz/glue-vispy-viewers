<template>
    <div class="glue-layer-scatter">
        <div class="text-subtitle-2 font-weight-bold">Color</div>
        <div>
            <v-select label="color" :items="color_mode_items" v-model="color_mode_selected" hide-details />
        </div>
        <template v-if="glue_state.color_mode === 'Linear'">
            <div>
                <v-select label="attribute" :items="cmap_attribute_items" v-model="cmap_attribute_selected" hide-details />
            </div>
            <div>
                <glue-float-field label="min" :value.sync="glue_state.cmap_vmin" />
            </div>
            <div>
                <glue-float-field label="max" :value.sync="glue_state.cmap_vmax" />
            </div>
            <div>
                <v-select label="colormap" :items="cmap_items" :value="glue_state.cmap" @change="set_colormap" hide-details/>
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="glue_state.alpha" hide-details />
        </div>
        <div class="text-subtitle-2 font-weight-bold">Points</div>
        <v-select label="size" :items="size_mode_items" v-model="size_mode_selected" hide-details />
        <template v-if="glue_state.size_mode === 'Linear'">
            <div>
                <v-select label="attribute" :items="size_attribute_items" v-model="size_attribute_selected" hide-details />
            </div>
            <div>
                <glue-float-field label="min" :value.sync="glue_state.size_vmin" />
            </div>
            <div>
                <glue-float-field label="max" :value.sync="glue_state.size_vmax" />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">size scaling</v-subheader>
            <glue-throttled-slider wait="300" min="0.1" max="10" step="0.01" :value.sync="glue_state.size_scaling"
                hide-details />
        </div>
        <div class="text-subtitle-2 font-weight-bold" :style="glue_state.markers_visible ? {} : {marginTop: '6px'}">Vectors</div>
        <div>
            <v-subheader class="pl-0 slider-label">show vectors</v-subheader>
            <v-switch v-model="glue_state.vector_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="glue_state.vector_visible">
            <div>
                <v-select label="vx" :items="vx_attribute_items" v-model="vx_attribute_selected" hide-details />
            </div>
            <div>
                <v-select label="vy" :items="vy_attribute_items" v-model="vy_attribute_selected" hide-details />
            </div>
            <div>
                <v-select label="vy" :items="vz_attribute_items" v-model="vz_attribute_selected" hide-details />
            </div>
        </template>
        <div class="text-subtitle-2 font-weight-bold" :style="glue_state.vector_visible ? {} : {marginTop: '6px'}">Errorbars</div>
        <div>
            <v-subheader class="pl-0 slider-label">show x errors</v-subheader>
            <v-switch v-model="glue_state.xerr_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="glue_state.xerr_visible">
            <div>
                <v-select label="xerr" :items="xerr_attribute_items" v-model="xerr_attribute_selected" hide-details />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">show y errors</v-subheader>
            <v-switch v-model="glue_state.yerr_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="glue_state.yerr_visible">
            <div>
                <v-select label="yerr" :items="yerr_attribute_items" v-model="yerr_attribute_selected" hide-details />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">show z errors</v-subheader>
            <v-switch v-model="glue_state.zerr_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="glue_state.zerr_visible">
            <div>
                <v-select label="zerr" :items="zerr_attribute_items" v-model="zerr_attribute_selected" hide-details />
            </div>
        </template>
    </div>
</template>
<script>
</script>
<style id="layer_scatter">
.glue-layer-scatter .v-subheader.slider-label {
    font-size: 12px;
    height: 16px;
    margin-top: 6px;
}
</style>
