<template>
  <div class="border p-2 my-2 bg-white rounded-md">
    <div class="flex justify-between">
      <h4 class="font-semibold text-proyecto-text ">
      Radio de búsqueda: {{ !isDisable ? actualRadius / 1000 + " km" : '' }}
      </h4>
    </div>

    <div class="flex justify-between items-center flex-wrap gap-2">

      <div class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
        <ButtonPrimary
        v-for="value in radius"
        :text="value + ' km'"
        @click="onRadiusClick(value)"
        :class="actualRadius == value*1000 ? 'bg-proyecto-accent' : ''" />
      </div>
      <div class="flex flex-col items-end">
        <ButtonPrimary v-if="showButton && !isDisable"
        :text="'Actualizar radio de búsqueda'"
        @click="updateRadiusPath"
        :icon_left="'fa-solid fa-rotate mr-2'" />
      </div>
    </div>
  </div>
  <div :style="props.styleContent">
    <l-map @click="onMapClick"   @mousemove="onMouseMove" :zoom="props.zoom" :center="props.center" :class="'border rounded-xl'">
      <l-tile-layer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      ></l-tile-layer>

      <l-control>
        <div class="bg-proyecto-bg p-2 bottom-1 rounded-md shadow-md text-proyecto-text border-1 text-xs font-semibold ">
          {{ coordinates ? coordinates : '' }}
        </div>
      </l-control>

      <l-marker  v-for="(m, index) in props.marks"
      :lat-lng="[m.lat, m.lon]"
      :key="index"
      :icon="customIconOrange">
        <l-popup :visible="true">
          {{ m.name }}
        </l-popup>
      </l-marker>

      <l-marker v-if="actualRadius && !isDisable"
      :lat-lng="radiusCenter"
      :icon="customIconRed">
      </l-marker>

      <l-circle
      v-if="actualRadius && !isDisable"
      :lat-lng="radiusCenter"
      :radius="actualRadius"
      color="orange">
      </l-circle>
    </l-map>
  </div>
</template>

<script setup>
    import { ref, defineEmits} from 'vue'
    import L from "leaflet";
    import "leaflet/dist/leaflet.css";
    import { LMap, LTileLayer, LMarker, LPopup, LControl, LCircle,  } from "@vue-leaflet/vue-leaflet";
    import { useRoute, useRouter } from 'vue-router';
    import ButtonPrimary from "./buttons/ButtonPrimary.vue"

    const showButton = ref(false)
    const radiusCenter = ref({lat: -34.92098577515593, lng: -57.95459747314454})
    const radius = [5, 10, 30, 50, 100]
    const actualRadius = ref(null)
    const coordinates = ref(null)
    const route = useRoute()
    const router = useRouter()

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

    const customIconRed=  L.icon({
        iconUrl:
          "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
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
        index: { default: true },
        isDisable: {default: false}
    })

    const emit = defineEmits(["changeMapState"])



    const calculateNewRadius = (r) => {
      return r * 1000
    }

    const onMapClick = (e) => {
      radiusCenter.value = e.latlng
      if (props.isDisable)
        emit("changeMapState", false)
      if (!actualRadius.value)
        actualRadius.value = 5*1000;
      showButton.value = true;
    }

    const onMouseMove = (e) => {
      coordinates.value = `Lat: ${parseFloat(e.latlng.lat).toFixed(3)} Lon: ${parseFloat(e.latlng.lng).toFixed(3)}`;
    }

    const onRadiusClick = (r) => {
      actualRadius.value = calculateNewRadius(r);
      if (props.isDisable)
        emit("changeMapState", false)
      showButton.value = true;
    }

    const updateRadiusPath = () => {
      router.push({
        path: route.path,
        query: {
          ...route.query,
          lat: radiusCenter.value.lat,
          lon: radiusCenter.value.lng ,
          radius: actualRadius.value / 1000,
        }
      })
    }

</script>
