<template>
    <section class="w-full">
        <div class="flex items-start gap-4 w-full justify-center border-b-2 pt-1 pb-3">
            <aside class="flex gap-4 flex-col">
                <h2 class="text-2xl font-bold">
                    {{ detalle.name }}
                </h2>
                <div class="flex gap-1 items-center  border-b-2 pb-2">
                    <Stars :rating="detalle.rating"></Stars>
                    <span class="text-lg font-semibold text-yellow-500">
                        ({{ detalle.count_rating }})
                    </span>
                </div>

                <div class="flex gap-1  border-b-2 pt-1 pb-2">
                    <IconLocation class="fill-red-700 w-3"></IconLocation>
                    <span>
                        {{ detalle.province }},
                    </span>
                    <span>
                        {{ detalle.city }}
                    </span>
                </div>
                <div class="flex gap-7">
                    <div>
                        <p class="font-semibold">Estado de conservación</p>
                        <span>
                            {{ detalle.state }}
                        </span>
                        <p class="font-semibold">Año de inagaruación</p>
                        <span class="">
                            {{ detalle.year }}
                        </span>
                    </div>
                    <div>
                        <p class="font-semibold">Categoria</p>
                        <span>
                            {{ detalle.category }}
                        </span>

                    </div>
                </div>
                <Tag :tags="detalle.tags"></Tag>
            </aside>
        </div>      
        <Acordion 
                :content="content">
        </Acordion>
    </section>
    <Map :lon="detalle.lon" :lat="detalle.lat" :name="detalle.name"></Map>
    <h3 class="text-2xl">Reseñas</h3>
</template>

<script setup>
    import { ref } from 'vue'
    import Stars from '@/components/Stars.vue'
    import IconLocation from '@/components/icons/IconLocation.vue'
    import Acordion from '@/components/Acordion.vue'
    import Tag from '@/components/Tag.vue'
    import Carrousel from '@/components/Carrousel.vue'
    import Map from '@/components/Map.vue'
    const detalle = ref({})
    detalle.value = {
        "name": "Sitio histórico Corrientes",
        "province": "Santiago del Estero",
        "city": "La Banda",
        "state": "Malo",
        "category": "Fortificación",
        "year": 1960,
        "rating": 4,
        "count_rating": 30,
        "tags": [
            "tag1",
            "tag2",   
            "tag3"
        ],
        "full_desc": "holaholaholaasdoasdasdasdadasdsadadasdasasdasdsadasdasdasdasdadadasdasdasdasdasdasdadasdasdad",
        "brief_desc": "asdasdasdasadasdsadasdasdasdasdaddasdasdadasdadas",
        "lat": 37.4124,
        "lon": 52.124
    }
    const content = [{id:1, header:'Descripción detallada', text:detalle.value.full_desc},{id:2, header:'Descripción breve', text:detalle.value.brief_desc}]
</script>       