<template>
    <form class="  ">
        <div class="flex items-center gap-3 flex-wrap ">

            <div class="flex flex-col gap-2 ">
                <select id="small" v-model="provinceValue" @click="fetchCities(provinceValue)" class="block max-w-96  p-2  text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    <option selected>Provincia</option>
                    <option :value="province.name" v-for="province in provinces">{{ province.name }}</option>
                </select>
                <select id="default" v-model="cityValue"  class="block w-96 p-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    <option selected>Ciudad</option>
                    <option :value="city.name" v-for="city in cities" >{{ city.name }}</option>
                </select>
            </div>

            <div class="flex flex-col gap-2">
                <div class="relative">
                    <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
                        </svg>
                    </div>
                    <input type="search" v-model="nameValue" id="search" class="w-96 p-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Nombre del sitio" />
                </div>
                    <div class="relative">
                    <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                        <svg class="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 20">
                            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"/>
                        </svg>
                    </div>
                    <input type="search" v-model="descrpitionValue" id="search" class="block w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Descripción breve"  />
                </div>        
            </div>
            <div class="flex flex-col gap-2">
                <div v-if="authStore.isAuthenticated" v-on:click="tags" class="w-96 p-2 border rounded-md text-sm bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    <input id="bordered-checkbox-1" v-model="favoriteValue" type="checkbox" value="" name="bordered-checkbox" class=" text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                    <label for="bordered-checkbox-1" class="w-full  ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Favoritos</label>
                </div>
                <div>
                    <select id="default" v-model="orderByValue" class="block w-96 p-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        <option selected>Ordenar por</option>
                        <option value="oldest">Últimos creados</option>
                        <option value="latest">Primeros creados</option>
                        <option value="rating-1-5">Reseñas 1-5 estrellas</option>
                        <option value="rating-5-1">Reseñas 5-1 estrellas</option>
                    </select>
                </div>
            </div>

            <div class="flex md:flex-col">
                <router-link :to="{query: { 
                                    ...(nameValue) && {name: nameValue},
                                    ...(descrpitionValue) && {description: descrpitionValue},
                                    ...(provinceValue != 'Provincia') && {province: provinceValue},
                                    ...(cityValue != 'Ciudad') && {city: cityValue},
                                    ...(tagsValue.length > 0) && {tags: tagsValue.join()},
                                    ...{page: 1},
                                    ...{favorites: favoriteValue},
                                    ...(orderByValue != 'Ordenar por') && {order_by: orderByValue},
                                    ...({lat: rout.query.lat}),
                                    ...({lon: rout.query.lon}),
                                    ...({radius: rout.query.radius})
                                    }}" class="text-white bg-proyecto-primary hover:bg-proyecto-accent focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Filtrar</router-link>
                <router-link @click="desibleMapClick" :to="{query: {}}" class="text-white  bg-proyecto-primary hover:bg-proyecto-accent focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Restaurar</router-link>
            </div>
        </div>
        <div>
            <select name="tags" id="tags" multiple>
                    <option v-for="tag in tags" :key="tag.id" :value="tag.slug">{{ tag.name }}</option>
            </select>
        </div>
    </form>

</template>

<script setup>
    import api from '@/api/axios'
    import { ref, watch, nextTick, onMounted, defineEmits } from 'vue'
    import { useRoute } from 'vue-router'
    import { useAuthStore } from '@/stores/auth'

    const authStore = useAuthStore()
    const emit = defineEmits(['disableMap'])
    const cityValue = ref("Ciudad")
    const nameValue = ref("")
    const descrpitionValue = ref("")
    const tagsValue = ref([])
    const favoriteValue = ref(false)
    const orderByValue = ref("Ordenar por")
    const provinceValue = ref("Provincia")
    const cities = ref([])
    const rout = useRoute()
    const props = defineProps(["provinces", "states", "page", "tags"])

    onMounted(() => initMultiSelect())
    watch(
        () => props.tags,
        async (newTags) => {
            if (newTags && newTags.length > 0) {
            await nextTick() 
            destroyMultiSelect()
            initMultiSelect()
            }
        },
        { immediate: true }
    )


    function destroyMultiSelect() {
        const prev = document.querySelector('.multi-select-tag')
        if (prev) prev.remove()
    }


    function initMultiSelect() {
        new MultiSelectTag('tags', {
            rounded: true,
            shadow: true,
            placeholder: 'Seleccionar tags',
            onChange(selected) {
                tagsValue.value = selected.map((e) => (e.id))
                console.log('Tags seleccionados:', tagsValue.value)
            }
        })

        const inputTag = document.getElementById('tag-input')

        if (inputTag) {
            inputTag.className = 'w-full'
            inputTag.setAttribute('readonly', '')
        }

        const dropdown = document.getElementById('dropdown')
        if (dropdown) dropdown.style.zIndex = '1200'
    }

    const fetchCities = async (provinceName) => {
        const province = props.provinces.find(p => p.name == provinceName)
        if (province) {
            const idProvince = province.id
            const { data } = await api.get(`provinces/${idProvince}/cities`)
            cityValue.value = "Ciudad"
            cities.value = data.data
        }
    }

    const desibleMapClick = () => {
        emit('disableMap', true)
    }

</script>
