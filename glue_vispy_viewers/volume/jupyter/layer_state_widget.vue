<template>
    <div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details class="margin-bottom: 16px" />
        </div>
        <template v-if="glue_state.color_mode === 'Linear'">
          <div>
              <v-select label="colormap" :items="cmap_items" :value="glue_state.cmap" @change="set_colormap" hide-details/>
          </div>
        </template>
        <template v-else>
          <div v-if="!subset">
              <v-select label="color" :items="color_mode_items" v-model="color_mode_selected" hide-details />
          </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" max="1" step="0.01" :value.sync="glue_state.alpha" hide-details />
        </div>
        <div>
            <glue-float-field label="min" :value.sync="glue_state.vmin" />
        </div>
        <div>
            <glue-float-field label="max" :value.sync="glue_state.vmax" />
        </div>
    </div>
</template>
<script>
    modules.export = {
        methods: {
            setAlpha(value) {
                this.glue_state.alpha = value;
            },
        },
    }
</script>
<style id="layer_volume">
    .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
