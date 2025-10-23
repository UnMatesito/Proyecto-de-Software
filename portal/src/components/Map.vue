<template>
    <div id="map">

    </div>
</template>

<script setup>
        import { onMounted } from 'vue'
        const props = defineProps(["lon", "lat", "name"])
        
        onMounted(() => {
            var map = L.map('map').setView([props.lat, props.lon], 13);

            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            }).addTo(map);
            
            L.marker([parseFloat(props.lat), parseFloat(props.lon)]).addTo(map)
                    .bindPopup(`${props.name}  <br> Latitud: ${parseFloat(props.lat).toFixed(4)} <br> Longitud: ${parseFloat(props.lon).toFixed(4)}`)
                    .openPopup();
        })

</script>
<style>
    #map { height: 60vh;
            max-width: 800px;
            width: 100%; 
            border-radius: 6px;
            border: 1px solid #c0bfbf;
        }
</style>