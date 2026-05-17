<template>
    <div class="glue-layer-scatter">
        <div class="text-subtitle-2 font-weight-bold">Color</div>
        <div>
            <v-select label="color" :items="color_mode_items" v-model="color_mode_selected" hide-details />
        </div>
        <template v-if="(color_mode_items[color_mode_selected] || {}).text === 'Linear'">
            <div>
                <v-select label="attribute" :items="cmap_att_items" v-model="cmap_att_selected" hide-details />
            </div>
            <div>
                <glue-float-field label="min" :value.sync="cmap_vmin" echo-type="float" />
            </div>
            <div>
                <glue-float-field label="max" :value.sync="cmap_vmax" echo-type="float" />
            </div>
            <div>
                <v-select label="colormap" :items="cmap_items" v-model="cmap" hide-details />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="alpha" echo-type="float" hide-details />
        </div>
        <div class="text-subtitle-2 font-weight-bold">Points</div>
        <v-select label="size" :items="size_mode_items" v-model="size_mode_selected" hide-details />
        <template v-if="(size_mode_items[size_mode_selected] || {}).text === 'Linear'">
            <div>
                <v-select label="attribute" :items="size_att_items" v-model="size_att_selected" hide-details />
            </div>
            <div>
                <glue-float-field label="min" :value.sync="size_vmin" echo-type="float" />
            </div>
            <div>
                <glue-float-field label="max" :value.sync="size_vmax" echo-type="float" />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">size scaling</v-subheader>
            <glue-throttled-slider wait="300" min="0.1" max="10" step="0.01" :value.sync="size_scaling" echo-type="float"
                hide-details />
        </div>
        <div class="text-subtitle-2 font-weight-bold" style="margin-top: 6px;">Vectors</div>
        <div>
            <v-subheader class="pl-0 slider-label">show vectors</v-subheader>
            <v-switch v-model="vector_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="vector_visible">
            <div>
                <v-select label="vx" :items="vx_att_items" v-model="vx_att_selected" hide-details />
            </div>
            <div>
                <v-select label="vy" :items="vy_att_items" v-model="vy_att_selected" hide-details />
            </div>
            <div>
                <v-select label="vy" :items="vz_att_items" v-model="vz_att_selected" hide-details />
            </div>
        </template>
        <div class="text-subtitle-2 font-weight-bold" :style="vector_visible ? {} : {marginTop: '6px'}">Errorbars</div>
        <div>
            <v-subheader class="pl-0 slider-label">show x errors</v-subheader>
            <v-switch v-model="xerr_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="xerr_visible">
            <div>
                <v-select label="xerr" :items="xerr_att_items" v-model="xerr_att_selected" hide-details />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">show y errors</v-subheader>
            <v-switch v-model="yerr_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="yerr_visible">
            <div>
                <v-select label="yerr" :items="yerr_att_items" v-model="yerr_att_selected" hide-details />
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">show z errors</v-subheader>
            <v-switch v-model="zerr_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="zerr_visible">
            <div>
                <v-select label="zerr" :items="zerr_att_items" v-model="zerr_att_selected" hide-details />
            </div>
        </template>
    </div>
</template>

<style id="layer_scatter">
.glue-layer-scatter .v-subheader.slider-label {
    font-size: 12px;
    height: 16px;
    margin-top: 6px;
}
</style>
