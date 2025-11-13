<script setup>
  import Card from '@/components/Card.vue';

  const props = defineProps({
    sites: {
      type: Array,
      required: true,
      default: () => []
    },
    isAuthenticated: {
      type: Boolean,
      required: true
    },
    isFavorite: {
      type: Function,
      required: true
    },
    toggleFavorite: {
      type: Function,
      required: false
    },
    hideFavoriteButton: {
      type: Boolean,
      required: false,
      default: false
    }
  });
</script>

<template>
  <ul v-if="props.sites.length" class="flex gap-3 sm:gap-4 overflow-x-auto scroll-smooth pb-4 scrollbar-hide lg:px-2">
    <li v-for="site in props.sites" :key="site.id" class="flex-none w-40 sm:w-48 md:w-56 lg:w-64">
      <Card
          :id="site.id"
          :name="site.name"
          :province="site.province"
          :city="site.city"
          :tags="site.tags || []"
          :state_of_conservation="site.state_of_conservation"
          :inauguration_year="site.inauguration_year"
          :average_rating="site.average_rating || 0"
          :category="site.category"
          :imagen="site.images?.[0]?.url || site.imagen"
          :is-favorite="props.isFavorite(site.id)"
          :is-authenticated="props.isAuthenticated"
          :hide-favorite-button="props.hideFavoriteButton"
          @toggle-favorite="props.toggleFavorite"
      ></Card>
    </li>
  </ul>
  <div v-else class="h-[200px] flex justify-center items-center">
    <p class="px-5 py-2 text-white bg-proyecto-primary/80 text-center rounded-full inline-flex font-semibold shadow-md select-none"> No hay Contenido</p>
  </div>
</template>