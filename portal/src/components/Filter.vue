<template>
    <form class="  ">
        <div class="flex items-center gap-3 flex-wrap ">
            <div class="flex flex-col gap-2 ">
                <select id="small" v-model="provinceValue" class="block max-w-96  p-2  text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    <option selected>Provincia</option>
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="FR">France</option>
                    <option value="DE">Germany</option>
                </select>
                <select id="default" v-model="cityValue" class="block w-96 p-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    <option selected>Ciudad</option>
                    <option value="US">United States</option>
                    <option value="CA">Canada</option>
                    <option value="FR">France</option>
                    <option value="DE">Germany</option>
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
                <div v-on:click="tagss" class="w-96 p-2 border rounded-md text-sm bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                    <input id="bordered-checkbox-1" v-model="favoriteValue" type="checkbox" value="" name="bordered-checkbox" class=" text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                    <label for="bordered-checkbox-1" class="w-full  ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">Favoritos</label>
                </div>
                <div>
                    <select id="default" v-model="orderByValue" class="block w-96 p-2 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        <option selected>Ordenar por</option>
                        <option value="US">Nombre A-Z</option>
                        <option value="CA">Nombre Z-A</option>
                        <option value="FR">Últimos creados</option>
                        <option value="DE">Primeros creados</option>
                        <option value="DE">Reseñas 1-5 estrellas</option>
                        <option value="DE">Reseñas 5-1 estrellas</option>
                    </select>
                </div>
            </div>

            <div class="flex md:flex-col">
                <router-link :to="{query: { 
                                    ...(nameValue) && {name: nameValue},
                                    ...(descrpitionValue) && {description: descrpitionValue},
                                    ...(provinceValue) && {province: provinceValue},
                                    ...(cityValue) && {city: cityValue},
                                    ...(tagsValue.length > 0) && {tags: tagsValue.join()},
                                    ...{page: rout.query.page || 1},
                                    ...(false) && {favorites: favoriteValue},
                                    ...({lat: rout.query.lat}),
                                    ...({lon: rout.query.lon}),
                                    ...({radius: rout.query.radius})
                                    }}" class="text-white bg-proyecto-primary hover:bg-proyecto-accent focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Filtrar</router-link>
                <router-link :to="{query: {}}" class="text-white  bg-proyecto-primary hover:bg-proyecto-accent focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition font-medium rounded-lg text-sm px-5 py-2.5 me-2 mb-2 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800">Restaurar</router-link>
            </div>
        </div>
        <div>
            <select name="tags" v-model="tagsValue" id="tags" multiple>
                    <option value="1">Afghanistan</option>
                    <option value="2" >Australia</option>
                    <option value="3">Germany</option>
                    <option value="4">Canada</option>
                    <option value="5">Russia</option>
            </select>
        </div>
    </form>

</template>

<script setup>
    import { ref, onMounted} from 'vue'
    import { useRoute } from 'vue-router'
    const provinceValue = ref("")
    const cityValue = ref("")
    const nameValue = ref("")
    const descrpitionValue = ref("")
    const tagsValue = ref([])
    const favoriteValue = ref(false)
    const order_by = ref("latest")
    const rout = useRoute()
    defineProps(["province", "states", "page"])
 
    onMounted(
        () => {
            new MultiSelectTag('tags', {
                rounded: true,   
                shadow: true,
                placeholder: "Seleccionar tags",
                onChange: function(selected) {
                    let transform = []
                    selected.forEach(data => transform.push(data.label));
                    tagsValue.value = transform
                    console.log(tagsValue.value.length)
                }
            });
            let inputTag = document.getElementById("tag-input")
            inputTag.className = "w-full"
            inputTag.setAttribute("readonly", "")
            document.getElementById("dropdown").setAttribute('style', 'z-index:1200');
        }
    )
    

</script>