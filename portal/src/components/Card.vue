<script setup>
    import IconFavorite from './icons/IconFavorite.vue'
    import IconLocation from './icons/IconLocation.vue'
    import IconBuild from './icons/IconBuild.vue'
    import Stars from './Stars.vue'

    const props = defineProps({
        id: Number,
        name: String,
        province: String,
        city: String,
        tags: Array,
        state_of_conservation: String,
        inauguration_year: Number,
        category: String,
        average_rating: {
            type: Number,
            default: 0
        },
        imagen: String,
        isFavorite: Boolean,
        isAuthenticated: Boolean,
        hideFavoriteButton: Boolean
    })

    const emit = defineEmits(['toggle-favorite'])

    const tags_to_show = props.tags?.slice(0, 5) || []
    const tags_left = props.tags?.length > 5 ? props.tags.length - 5 : 0
    const urlImg = props.imagen  || "https://www.infobae.com/resizer/v2/https%3A%2F%2Fs3.amazonaws.com%2Farc-wordpress-client-uploads%2Finfobae-wp%2Fwp-content%2Fuploads%2F2019%2F02%2F13105727%2FMarcha-Movimientos-sociales-Obelisco-3.jpeg?auth=98ea526ca284a14796ed1e27f354b65dc880d7115c2a54ed2e28ebf23b40563f&smart=true&width=1200&height=675&quality=85"
    const alt = props.imagen || props.name

    const toggleFavorite = (siteId) => {
      console.log('Toggle favorite for site:', siteId)
      console.log('Average rating:', props.average_rating)
      emit('toggle-favorite', siteId)
    }
</script>

<template>
    <a :href="`/sites/${props.id}`" class="rounded-lg relative flex flex-col gap-0.5 sm:gap-1 overflow-hidden w-full cursor-pointer shadow-lg hover:shadow-2xl transition duration-300 ease-in-out bg-white hover:shadow-proyecto-accent/80 h-full">

        <button v-if="props.isAuthenticated" @click.prevent.stop="toggleFavorite(props.id)" :class="{'fill-red-600': props.isFavorite, 'fill-gray-500': !props.isFavorite, 'hidden': props.hideFavoriteButton}" class="absolute left-1.5 top-1.5 sm:left-2 sm:top-2 bg-white/90 backdrop-blur-sm p-1 sm:p-1.5 border-0 rounded-full text-center hover:opacity-75 hover:fill-red-600 transition-all duration-400 ease-in-out z-10 shadow-md">
            <IconFavorite class="w-3.5 h-3.5 sm:w-5 sm:h-5 block"></IconFavorite>
        </button>

        <div class="relative w-full aspect-[4/3] sm:aspect-video">
            <img class="absolute inset-0 w-full h-full object-cover" :src="urlImg" :alt="alt">
        </div>

        <div class="w-full mt-1 sm:mt-2 flex justify-center">
          <Stars :rating="props.average_rating || 0"></Stars>
        </div>

        <div class="p-2 sm:p-4 flex flex-col gap-1 sm:gap-2">
            <div class="flex gap-1 sm:gap-1.5 items-center">
                <IconBuild class="fill-slate-400 w-3.5 h-3.5 sm:w-4 sm:h-4"></IconBuild>
                <h3 class="font-semibold text-xs sm:text-base line-clamp-2 leading-tight sm:leading-normal">
                    {{ props.name }}
                </h3>
            </div>
            <div class="flex flex-row gap-1 sm:gap-1.5 items-center">
                <IconLocation class="fill-slate-400 w-3.5 h-3.5 sm:w-4 sm:h-4"></IconLocation>
                <p class="text-[10px] sm:text-sm leading-tight">{{ `${props.province}, ${props.city}` }}</p>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 gap-1 sm:gap-3 mt-0.5 sm:mt-0 justify-items-center">
                <div class="text-center sm:text-left">
                    <span class="text-proyecto-primary/80 text-[10px] sm:text-xs font-semibold block leading-tight">Estado</span>
                    <p class="text-gray-700 text-[10px] sm:text-sm font-semibold leading-tight">{{ props.state_of_conservation }}</p>
                </div>
                <div class="text-center sm:text-left">
                    <span class="text-proyecto-primary/80 text-[10px] sm:text-xs font-semibold block leading-tight">Año</span>
                    <p class="text-gray-700 text-[10px] sm:text-sm font-semibold leading-tight">{{ props.inauguration_year }}</p>
                </div>
                <div class="text-center sm:text-left col-span-2 sm:col-span-1">
                    <span class="text-proyecto-primary/80 text-[10px] sm:text-xs font-semibold block leading-tight">Categoría</span>
                    <p class="text-gray-700 text-[10px] sm:text-sm font-semibold leading-tight">{{ props.category }}</p>
                </div>
            </div>

            <div class="flex gap-1 sm:gap-2 text-blue-700 flex-wrap border-t-2 pt-1 sm:pt-2 pb-0.5 sm:pb-1">
                <span v-for="tag in tags_to_show" :key="tag" class="inline-flex items-center bg-blue-50 text-blue-500 text-[10px] sm:text-xs font-semibold px-1.5 sm:px-2.5 py-0.5 border sm:border-2 rounded-full border-blue-500 whitespace-nowrap">{{ tag }}</span>
                <span v-if="tags_left > 0" class="inline-flex items-center bg-blue-100 text-blue-500 text-[10px] sm:text-xs font-bold px-1.5 sm:px-2.5 py-0.5 border sm:border-2 rounded-full border-blue-500">{{ `+${tags_left}` }}</span>
            </div>
        </div>
    </a>
</template>
