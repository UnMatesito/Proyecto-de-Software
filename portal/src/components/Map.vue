<template>
    <div id="map">

    </div>
</template>

<script setup>
        import { onMounted, watch } from 'vue'
        const props = defineProps(["long", "lat", "name"])
        
        watch(props, () => {
            var map = L.map('map').setView([props.lat, props.long], 13);

            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            }).addTo(map);
            
            L.marker([parseFloat(props.lat), parseFloat(props.long)]).addTo(map)
                    .bindPopup(`${props.name}  <br> Latitud: ${parseFloat(props.lat).toFixed(4)} <br> Longitud: ${parseFloat(props.long).toFixed(4)}`)
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