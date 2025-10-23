<template>
    <section class="flex items-center">
        <Carrousel></Carrousel>
        <aside class="flex gap-5 flex-col">
            <h2 class="text-2xl font-bold">
                {{ detalle.name }}
            </h2>
            <div class="flex gap-1 items-center">
                <Stars :rating="detalle.rating"></Stars>
                <span class="text-lg font-semibold text-yellow-500">
                    ({{ detalle.count_rating }})
                </span>
            </div>
            <div class="flex gap-1">
                <IconLocation class="fill-red-700 w-3"></IconLocation>
                <span>
                    {{ detalle.province }},
                </span>
                <span>
                    {{ detalle.city }}
                </span>
            </div>
                <div>
                    <p class="font-semibold">Estado de conservación</p>
                    <span>
                        {{ detalle.state }}
                    </span>
                </div>
                <div>
                    <p class="font-semibold">Categoria</p>
                    <span>
                        {{ detalle.category }}
                    </span>
                </div>
            <Acordion></Acordion>
            <Tag :tags="detalle.tags"></Tag>
        </aside>
    </section>
</template>

<script setup>
    import { ref } from 'vue'
    import Stars from '@/components/Stars.vue'
    import IconLocation from '@/components/icons/IconLocation.vue'
    import Acordion from '@/components/Acordion.vue'
    import Tag from '@/components/Tag.vue'
    import Carrousel from '@/components/Carrousel.vue'
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
        "briev_desc": "asdasdasdasadasdsadasdasdasdasdaddasdasdadasdadas"
    }
</script>       