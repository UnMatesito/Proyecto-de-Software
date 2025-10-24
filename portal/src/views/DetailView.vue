<template>
    <router-link to="/sites"  type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none gap-2 focus:ring-blue-300 font-medium rounded-lg text-sm px-3 py-2 text-center inline-flex items-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
         <IconArrowLeft class="w-3.5 h-3.5 ms-2 fill-white"> </IconArrowLeft>
        Volver
    </router-link >
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
                            {{ detalle.state_of_conservation }}
                        </span>
                        <p class="font-semibold">Año de inagaruación</p>
                        <span class="">
                            {{ detalle.inauguration_year }}
                        </span>
                    </div>
                    <div>
                        <p class="font-semibold">Categoria</p>
                        <span>
                            {{ detalle.category }}
                        </span>

                    </div>
                </div>
            </aside>
        </div>      
        <Acordion 
                :content="content">
        </Acordion>
    </section>
    <Map :long="detalle.long" :lat="detalle.lat" :name="detalle.name"></Map>
    <h3 class="text-2xl">Reseñas</h3>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import Stars from '@/components/Stars.vue'
    import IconLocation from '@/components/icons/IconLocation.vue'
    import Acordion from '@/components/Acordion.vue'
    import Tag from '@/components/Tag.vue'
    import Carrousel from '@/components/Carrousel.vue'
    import IconArrowLeft from '@/components/icons/IconArrowLeft.vue'
    import Map from '@/components/Map.vue'
    import api from '@/api/axios'
    import { useRoute } from 'vue-router';
    const route  = useRoute()
    const detalle = ref({})
    const content = ref([])
    const reviews = ref({})
    const fetchDetalleSitio = async () => {
        try {
            const { data } = await api.get(`${route.path}`)
            detalle.value = data
            content.value = [{id:1, header:'Descripción detallada', text:detalle.value.description},{id:2, header:'Descripción breve', text:detalle.value.short_description}]
        } catch (error) {
            console.log(error)
        }
    }
    const fetchReviews = async () => {
        try {
            const { data } = await api.get(`${route.path}/reviews`)
            reviews.value = data
            console.log(data)
        } catch {

        }
    }
    onMounted(()=> {
        fetchDetalleSitio()
        fetchReviews()
    } )
</script>    