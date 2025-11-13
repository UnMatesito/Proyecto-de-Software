<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import Card from "@/components/Card.vue";
import { useAuthStore } from '@/stores/auth.js';
import { useSitesStore } from '@/stores/sites.js';
import { useFavoritesStore } from '@/stores/favorites.js';

defineProps({
    title: {
      type: String,
      required: true
    }
  });

const authStore = useAuthStore();
const sitesStore = useSitesStore();
const favoritesStore = useFavoritesStore();
const { isAuthenticated } = storeToRefs(authStore);

const apiMessage = ref('');

const sites = computed(() => sitesStore.getTopSites(10));

const isFavorite = (siteId) => {
  return favoritesStore.isFavorite(siteId);
};

const toggleFavorite = async (siteId) => {
  try {
    await favoritesStore.toggleFavorite(siteId);
  } catch (error) {
    console.error('Error al modificar favoritos:', error);
  }
};

const fetchSites = async () => {
  try {
    await sitesStore.fetchSites();
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API';
    console.error(error);
  }
};

const fetchFavorites = async () => {
  try {
    await favoritesStore.fetchFavorites();
  } catch (error) {
    console.error('Error al obtener favoritos:', error);
  }
};

onMounted(async () => {
  await fetchSites();
  await fetchFavorites();
});

watch(
  () => isAuthenticated.value,
  async (loggedIn) => {
    if (loggedIn) {
      await fetchFavorites();
    }
  }
);
</script>

<template>
  <div class="mb-8">
    <div class="flex flex-row justify-between items-center mb-4">
        <h2 class="text-2xl sm:text-4xl text-proyecto-primary font-semibold">{{ title }}</h2>
        <a href="#" class="text-sm sm:text-md font-semibold hover:bg-proyecto-primary hover:text-white rounded-full px-2.5 sm:px-4 py-1 sm:py-2 transition-colors duration-400">Ver Todos <i class="fa-solid fa-chevron-right ml-1"></i></a>
    </div>
    <div v-if="apiMessage" class="mb-4 rounded-md bg-red-100 px-4 py-2 text-sm text-red-700">
      {{ apiMessage }}
    </div>
    <ul v-if="sites.length" class="flex gap-3 sm:gap-4 overflow-x-auto scroll-smooth pb-4 scrollbar-hide lg:px-2">
      <li v-for="site in sites" :key="site.id" class="flex-none w-40 sm:w-48 md:w-56 lg:w-64">
        <Card
            :id="site.id"
            :name="site.name"
            :province="site.province"
            :city="site.city"
            :tags="site.tags"
            :state_of_conservation="site.state_of_conservation"
            :inauguration_year="site.inauguration_year"
            :category="site.category"
            :imagen="site.imagen"
            :is-favorite="isFavorite(site.id)"
            :is-authenticated="isAuthenticated"
            @toggle-favorite="toggleFavorite"
        ></Card>
      </li>
    </ul>
    <div v-else class="h-[200px] flex justify-center items-center">
      <p class="px-5 py-2 text-white bg-proyecto-primary/80 text-center rounded-full inline-flex font-semibold shadow-md select-none"> No hay Contenido</p>
    </div>
  </div>
</template>
