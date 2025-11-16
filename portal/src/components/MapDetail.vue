<template>
  <div style="height:600px; width:100%">
    <l-map ref="map" :zoom="zoom" :center="mark" :class="'border rounded-xl'">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        layer-type="base"
        name="OpenStreetMap"
      ></l-tile-layer>

      <l-marker  
        :lat-lng="mark"
        :icon="customIconOrange">
        <l-popup :visible="true">
          {{ markName }}
        </l-popup>
      </l-marker>
    </l-map>
  </div>
</template>

<script setup>
    import L from "leaflet";
    import "leaflet/dist/leaflet.css";
    import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
    const customIconOrange =  L.icon({
        iconUrl:
          "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-orange.png",
        shadowUrl:
          "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41],
      })

    const props = defineProps({
        zoom: {
            default: 13
        },
        mark: {
            default: []
        },
        markName: {
            default: ''
        }
    })

</script>

<style>
</style>