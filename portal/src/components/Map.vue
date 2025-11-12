<template>
  <div :style="props.styleContent">
    <l-map @update:zoom="zoomUpdated" @update:center="centerUpdated" @update:bounds="" :zoom="props.zoom" :center="props.center" :class="'border rounded-xl'">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      ></l-tile-layer>
      <l-control>
        <ButtonPrimary v-if="showButton" :text="'Actualizar radio de busqueda'" @click="updateRedius" ></ButtonPrimary>
      </l-control>
      <l-marker  v-for="(m, index) in props.marks" 
      :lat-lng="[m.lat, m.long]"
      :key="index"
      :icon="customIcon">
        <l-popup :visible="true">{{ m.name }}</l-popup>
      </l-marker>
      <l-circle :lat-lng="radiusCenter" :radius="radius" color="orange">

      </l-circle>
    </l-map>
  </div>
</template>

<script setup>
    import { ref } from 'vue'
    import L, { map } from "leaflet";
    import "leaflet/dist/leaflet.css";
    import { LMap, LTileLayer, LMarker, LPopup, LControl, LCircle } from "@vue-leaflet/vue-leaflet";
    import ButtonPrimary from "./buttons/ButtonPrimary.vue";

    const showButton = ref(false)
    const radiusCenter = ref([-34.9205, -57.9536])
    const radiusCenterHelper = ref([-34.9205, -57.9536])
    const radius = ref(0)
    const zoomRadius = ref(13)
    
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
        name : { default: "site name" },
        styleContent: { default: "" },
        index: { default: true }
    })

    const calculateNewRadius = () => {
      const minRadius = 50;
      const maxRadius = 5000000;
      const referenceRadius = 500;
      const referenceZone = 13;
      const scale = Math.pow(2, referenceZone - zoomRadius.value);
      return Math.round(Math.max(minRadius, Math.min(maxRadius, referenceRadius * scale)))
    }
    
    const zoomUpdated = (newZoom) =>{
      zoomRadius.value = newZoom;
      console.log(newZoom)
      showButton.value = true;
    }  
    
    const centerUpdated = (newCenter) => { 
      radiusCenterHelper.value = [newCenter.lat, newCenter.lng];
      showButton.value = true;
    }
    
    const updateRedius = async () => {
      radiusCenter.value = radiusCenterHelper.value;
      radius.value = calculateNewRadius();
      showButton.value = false;
    }

</script>