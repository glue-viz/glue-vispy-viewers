<template>
    <div>
        <div>
            <v-select label="attribute" :items="attribute_items" v-model="attribute_selected" hide-details class="margin-bottom: 16px" />
        </div>
        <div v-if="!subset">
            <v-select label="color mode" :items="color_mode_items" v-model="color_mode_selected" hide-details />
        </div>
        <template v-if="(color_mode_items[color_mode_selected] || {}).text === 'Linear'">
          <div>
              <v-select label="colormap" :items="cmap_items" v-model="cmap" hide-details />
          </div>
        </template>
        <div>
           <v-select label="stretch" :items="stretch_items" v-model="stretch_selected" hide-details />
       </div> 
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" max="1" step="0.01" :value.sync="alpha" echo-type="float" hide-details />
        </div>
        <div>
            <glue-float-field label="min" :value.sync="v_min" echo-type="float" />
        </div>
        <div>
            <glue-float-field label="max" :value.sync="v_max" echo-type="float" />
        </div>
        <template v-if="true">
          <v-subheader>Cutting plane</v-subheader>
          <div v-if="!subset">
              <v-select label="color mode" :items="cut_plane_color_mode_items" v-model="cut_plane_color_mode_selected" hide-details />
          </div>
          <template v-if="(cut_plane_color_mode_items[cut_plane_color_mode_selected] || {}).text === 'Linear'">
            <div>
                <v-select label="colormap" :items="cmap_items" v-model="cut_plane_cmap" hide-details />
            </div>
          </template>
          <template v-else>
            <v-subheader class="pl-0 slider-label">color</v-subheader>
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
                    <v-color-picker v-model="cut_plane_color" echo-type="text" ></v-color-picker>
                </div>
            </v-menu>
          </template>
        </template>
    </div>
</template>

<style id="layer_volume">
    .v-subheader.slider-label {
        font-size: 12px;
        height: 16px;
    }
</style>
