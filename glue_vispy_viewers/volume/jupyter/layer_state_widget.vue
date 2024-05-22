<template>
    <div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details class="margin-bottom: 16px" />
        </div>
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
