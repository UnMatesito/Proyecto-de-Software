<script setup>
    import IconFavorite from './icons/IconFavorite.vue'
    import IconLocation from './icons/IconLocation.vue'
    import IconBuild from './icons/IconBuild.vue'
    import Stars from './Stars.vue'
    const props = defineProps(["name", "province", "city", "tags", "state_of_conservation", "inauguration_year", "category", "imagen"])
    const tags_to_show = props.tags.slice(0, 5)
    const tags_left = props.tags.length > 5 ? props.tags.length - 5 : 0
    const urlImg = props.imagen  || "https://www.infobae.com/resizer/v2/https%3A%2F%2Fs3.amazonaws.com%2Farc-wordpress-client-uploads%2Finfobae-wp%2Fwp-content%2Fuploads%2F2019%2F02%2F13105727%2FMarcha-Movimientos-sociales-Obelisco-3.jpeg?auth=98ea526ca284a14796ed1e27f354b65dc880d7115c2a54ed2e28ebf23b40563f&smart=true&width=1200&height=675&quality=85"
    const alt = props.imagen || props.name
</script>

<template>
    <div class=" rounded-lg relative flex flex-col gap-1 overflow-hidden md:max-w-64 cursor-pointer shadow-lg hover:shadow-2xl transition duration-300 ease-in-out bg-white hover:shadow-proyecto-accent/80">
        <span class="absolute left-1 top-1 bg-slate-200 p-1.5 border-0 rounded-full fill-gray-500 text-center hover:opacity-75 hover:fill-red-600 transition-all duration-400 ease-in-out">
            <IconFavorite class="w-5 block"></IconFavorite>
        </span>
         <img class="object-cover " :src="urlImg" :alt ="alt">
        <div class="w-full pt-2 flex justify-center">
          <Stars rating="1" class=""></Stars>
        </div>
        <div class="p-2 flex flex-col gap-1">
            <div class="flex gap-1 items-center">
                <IconBuild class="fill-slate-400 w-4 h-4"></IconBuild>
                <h3 class="font-semibold">
                    {{ props.name }}
                </h3>
            </div>
            <div class="flex flex-row gap-1 items-center">
                <span class="font-sans flex items-center justify-between gap-1">
                    <IconLocation class="fill-slate-400 w-4 h-4"></IconLocation>
                </span>
                <p class="text-sm">{{ `${props.province}, ${props.city}` }}</p>
            </div>
            <div class="flex gap-1 justify-between">
                <div>
                    <span class="text-proyecto-primary/80 text-sm font-semibold">Estado</span>
                    <p  class="text-gray-700 text-sm font-semibold">{{ props.state_of_conservation }}</p>
                </div>
                <div>
                    <span class="text-proyecto-primary/80 text-sm font-semibold">Año</span>
                    <p  class="text-gray-700 text-sm font-semibold">{{ props.inauguration_year }}</p>
                </div>
                <div>
                    <span class="text-proyecto-primary/80 text-sm font-semibold">Categoria</span>
                    <p class="text-gray-700 text-sm font-semibold">{{ props.category }}</p>
                </div>
            </div>
            <div class="flex gap-2 text-blue-700 flex-wrap border-t-2 pt-1">
                <span v-for="tag in tags_to_show" class="inline-flex items-center bg-blue-50 text-blue-500 text-xs font-semibold px-2.5 py-0.5 border-2 rounded-full border-blue-500">{{ tag }}</span>
                <span v-if="tags_left > 0" class="inline-flex items-center bg-blue-100 text-blue-500 text-xs font-bold px-2.5 py-0.5 border-2 rounded-full border-blue-500">{{ `+${tags_left}` }}</span>
            </div>
        </div>
    </div>
</template>
