<template>
  <div :style="props.styleContent">
    <l-map :zoom="props.zoom" :center="props.center" :class="'border rounded-xl'">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      ></l-tile-layer>
        {{ props.center }}
      <l-marker  v-for="(m, index) in props.marks" 
      :lat-lng="[m.lat, m.long]"
      :key="index"
      :icon="customIcon">
        <l-popup :visible="true">{{ m.name }}</l-popup>
      </l-marker>
    </l-map>
  </div>
</template>

<script setup>
    import L, { map } from "leaflet";
    import "leaflet/dist/leaflet.css";
    import { LMap, LTileLayer, LMarker, LPopup } from "@vue-leaflet/vue-leaflet";
    const customIcon =  L.icon({
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
        center: { default: [-34.9205, -57.9536] }, 
        zoom : { default: 13 }, 
        marks : { default: [] },
        name : { default: "site name"},
        styleContent: {default: ""}
    })
</script>
