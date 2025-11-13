<template>

    <div class="flex flex-col items-center justify-center max-w-[1200px] w-full">

        <section class="w-full p-3 max-w-screen-xl ">
            <ButtonPrimary :text="'Volver'" :icon_left="'fa-solid fa-arrow-left mr-2'" :link="'/sites'" :class="'my-4'"/> 
            <div class="flex items-start gap-4 w-full  pt-1 pb-3 flex-wrap relative" >
                <Carrousel/>
                <aside class="flex gap-4 flex-col max-w-[300px]">
                    <h2 class="text-2xl font-bold">
                        {{ detalle.name }}
                    </h2>
                    <div class="flex gap-1 items-center  border-b-2 pb-2">
                        <Stars :rating="detalle.rating" :class="'w-32'"></Stars>
                        <span class="text-lg font-semibold text-yellow-500">
                            ({{ detalle.count_rating || 0}})
                        </span>
                    </div>

                    <div class="flex gap-1 border-b-2 pt-1 pb-2 ">
                        <IconLocation class="fill-red-700 w-4"></IconLocation>
                        <div>
                        <span class="font-semibold text-gray-500">  
                            {{ detalle.province }},
                        </span>
                        <span class="font-semibold text-gray-500">
                            {{ detalle.city }}
                        </span>
                        </div>

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
                            <p class="font-semibold">Subido</p>
                            <span>
                                {{ detalle.inserted_at }}
                            </span>
                        </div>
                    </div> 
                    <div class="flex justify-between gap-2">
                        <ButtonPrimary :text="'Reseñas'" :icon_left="'fa-solid fa-arrow-down mr-2'" @click="scrollToReviews" > </ButtonPrimary>
                        <ButtonPrimary :text="'Ver en el mapa'" :icon_left="'fa-solid fa-arrow-down mr-2'" @click="scrollToMap" > </ButtonPrimary>
                    </div>
                </aside>
            </div>      
            <Acordion 
            :content="content"/>       
        </section>
        <div class="w-full max-w-[1200px] flex flex-col gap-3 mt-3">
            <h3 class="text-3xl text-proyecto-accent">Locación</h3>
            <div id="map">
                <Map v-if="detalle.name" 
                styleContent="height:400px;  width: 100%" 
                :marks="[{name: detalle.name, lat: detalle.lat, long: detalle.long}]" 
                :center="[detalle.lat, detalle.long]"></Map>
            </div>
        </div>
        <section class="w-full max-w-[1200px] flex flex-col gap-3 mt-3" >
            <h3 class="text-3xl text-proyecto-accent">Reseñas</h3>
            <ButtonPrimary :text="'Dar reseña'" :icon_left="'fa-solid fa-plus mr-2'" class="max-w-36 w-auto"> </ButtonPrimary>
            <Review v-for="r in reviews" 
            :user_name="r.user_name" 
            :user_email="r.user_email" 
            :text="r.comment" 
            :created_at="r.inserted_at" 
            :rating="r.rating"/>
            <p v-if="detalle.page > 1" @click="fetchReviews()" class="text-proyecto-primary font-semibold cursor-pointer hover:text-proyecto-accent transition-all ease-in-out">Ver más reseñas...</p>
        </section>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import Stars from '@/components/Stars.vue'
    import IconLocation from '@/components/icons/IconLocation.vue'
    import Acordion from '@/components/Acordion.vue'
    import Tag from '@/components/Tag.vue'
    import Carrousel from '@/components/Carrousel.vue'
    import api from '@/api/axios'
    import Review from '@/components/Review.vue'
    import ButtonPrimary from '@/components/buttons/ButtonPrimary.vue'
    import Map from '@/components/Map.vue'
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
            detalle.value = {...detalle.value, 'inserted_at': detalle.value.inserted_at.slice(0,  detalle.value.inserted_at.indexOf("T")).replaceAll("-", "/")}
            content.value = [{id:1, header:'Descripción detallada', text:detalle.value.description},{id:2, header:'Descripción breve', text:detalle.value.short_description}]
        } catch (error) {
            console.log(error)
        }
    }
    const fetchReviews = async () => {
        try {
            const response = await api.get(`${route.path}/reviews`)
            console.log(response.data.data)
            reviews.value = response.data.data
            page.value++
            console.log(reviews.value)
        } catch {

        }
    }
    onMounted(()=> {
        fetchDetalleSitio()
        fetchReviews()
    })

    const scrollToMap = () => {
        const map = document.getElementById('map');
        map.scrollIntoView({ behavior: "smooth" });
    }
    const scrollToReviews = () => {
        const reviews = document.getElementById('reviews');
        reviews.scrollIntoView({ behavior: "smooth" });
    }
</script>    