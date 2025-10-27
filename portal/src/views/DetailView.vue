<template>
    <router-link to="/sites"  type="button" class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none gap-2 focus:ring-blue-300 font-medium rounded-lg text-sm px-3 py-2 text-center inline-flex items-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
         <IconArrowLeft class="w-3.5 h-3.5 ms-2 fill-white"> </IconArrowLeft>
        Volver
    </router-link >
    <section class="w-full p-3 max-w-screen-xl">
        <div class="flex items-start gap-4 w-full justify-center border-b-2 pt-1 pb-3 flex-wrap">
            <Carrousel></Carrousel>
            <aside class="flex gap-4 flex-col">
                <h2 class="text-2xl font-bold">
                    {{ detalle.name }}
                </h2>
                <div class="flex gap-1 items-center  border-b-2 pb-2">
                    <Stars :rating="detalle.rating"></Stars>
                    <span class="text-lg font-semibold text-yellow-500">
                        ({{ detalle.count_rating || 0}})
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
    <div class="w-4/6 max-w-full flex flex-col gap-3 mt-3">
        <h3 class="text-2xl bg-proyecto-accent p-3 text-white">Locación</h3>
        <Map :long="detalle.long" :lat="detalle.lat" :name="detalle.name"></Map>
    </div>
    <section class="w-4/6 max-w-full flex flex-col gap-3 mt-3" >
        <h3 class="text-2xl bg-proyecto-accent p-3 text-white">Reseñas</h3>
        <div>
            <Review v-for="avatar in reviews" :name="avatar.name" :email="avatar.email" :text="avatar.text" :created_at="avatar.created_at"></Review>
        </div>
        <p v-if="detalle.page > 1" @click="fetchReviews()" class="text-proyecto-primary font-semibold cursor-pointer hover:text-proyecto-accent transition-all ease-in-out">Ver más reseñas...</p>
    </section>
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
    import Review from '@/components/Review.vue'
    import { useRoute } from 'vue-router';
    const route  = useRoute()
    const detalle = ref({})
    const content = ref([])
    const reviews = ref([])
    const page = ref(1)

    reviews.value = [ { name: "Tobias", 
    email: "palumbotobias@gmail.com", 
    text: "LoremLorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing ",
    created_at: "2025-10-22T00:38:28.842385Z" } ] 
    const fetchDetalleSitio = async () => {
        try {
            const { data } = await api.get(`${route.path}`)
            detalle.value = data
            console.log(data)
            content.value = [{id:1, header:'Descripción detallada', text:detalle.value.description},{id:2, header:'Descripción breve', text:detalle.value.short_description}]
        } catch (error) {
            console.log(error)
        }
    }

    const fetchReviews = async () => {
        try {
            const { data } = await api.get(`${route.path}/reviews/${page}`)
            reviews.value = data
            page.value++
        } catch {

        }
    }
    onMounted(()=> {
        fetchDetalleSitio()
        fetchReviews()
    } )
</script>    