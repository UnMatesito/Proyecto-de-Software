<script setup>
    const props = defineProps(["name", "province", "city", "tags", "state_of_conservation", "inaguration_year", "category", "imagen"])
    const tags_to_show = props.tags.slice(0, 5)
    const tags_left = props.tags.length > 5 ? props.tags.length - 5 : 0
</script>

<template>
    <div class=" rounded-lg relative flex flex-col gap-1 overflow-hidden max-w-64 cursor-pointer shadow-lg">
        <span class="absolute left-1 top-1 bg-slate-200 p-1 border-0 rounded-full w-9 text-center hover:opacity-75 hover:text-red-700 transition-opacity duration-300 ease-in-out"> 
            <i class="fa-regular fa-heart text-xl "></i>
        </span>
        <img class="object-cover" :src="props.imagen.url" :alt ="props.imagen.title">
        <div class="p-2 flex flex-col gap-1">
            <h3 class="font-semibold"><i class="fa-solid fa-building-columns  text-yellow-500"></i> {{ props.name }}</h3>
            <div>
                <span class=" font-sans ">
                    <i class="fa-solid fa-location-dot text-red-700"></i> 
                    {{ `${props.province}, ${props.city}` }}
                </span>
            </div>
            <div class="flex gap-1 justify-between">
                <div>
                    <span class="text-gray-500 text-sm font-semibold">Estado</span>
                    <p value="" class="text-gray-700 text-sm font-semibold">{{ props.state_of_conservation }}</p>
                </div>
                <div>
                    <span class="text-gray-500 text-sm font-semibold">Año</span>
                    <p value="" class="text-gray-700 text-sm font-semibold">{{ props.inaguration_year }}</p>
                </div>
                <div>
                    <span class="text-gray-500 text-sm font-semibold">Categoria</span>
                    <p class="text-gray-700 text-sm font-semibold">{{ props.category }}</p>
                </div>
            </div>
            <div class="flex gap-2 text-blue-700 flex-wrap border-t-2 pt-1">
                <span  v-for="tag in tags_to_show" class="inline-flex items-center bg-blue-300 text-sky-950 text-xs font-bold px-2.5 py-0.5 border-2 rounded-full ">{{ tag }}</span>
                <span  v-if="tags_left > 0" class="inline-flex items-center bg-blue-300 text-sky-950 text-xs font-bold px-2.5 py-0.5 border-2 rounded-full ">{{ `+${tags_left}` }}</span>
            </div>
        </div>
    </div>
</template>