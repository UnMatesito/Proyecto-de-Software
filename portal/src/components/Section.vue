<script setup>

import Card from "@/components/Card.vue";
import api from "@/api/axios.js";
import {onMounted, ref} from "vue";
import { useAuthStore } from '@/stores/auth.js';

const sites = ref([]);
const favorites = ref([]);
const apiMessage = ref('');

const authStore = useAuthStore();

const props = defineProps({
    title: {
      type: String,
      required: true
    }
  });

  const fetchSites = async () => {
      try {
        const { data } = await api.get("/sites")
        sites.value = data.data.slice(0, 10)
      } catch (error) {
        apiMessage.value = '❌ No se pudo conectar con la API'
        console.error(error)
      }
  };

  const fetchFavorites = async () => {
    // Solo intentar cargar favoritos si está autenticado
    if (!authStore.isAuthenticated) {
      favorites.value = [];
      return;
    }

    try {
      const { data } = await api.get("/me/favorites");
      favorites.value = data.data.map(site => site.id);
      console.log('Favoritos del usuario:', favorites.value);
    } catch (error) {
      favorites.value = [];
      console.error('Error al obtener favoritos:', error);
    }
  };

  const isFavorite = (siteId) => {
    return favorites.value.includes(siteId)
  };

  const toggleFavorite = async (siteId) => {
    try {
      if (isFavorite(siteId)) {
        await api.delete(`/sites/${siteId}/favorite`)
        favorites.value = favorites.value.filter(id => id !== siteId)
        console.log(`Sitio ${siteId} eliminado de favoritos`)
      } else {
        await api.put(`/sites/${siteId}/favorite`)
        favorites.value.push(siteId)
        console.log(`Sitio ${siteId} agregado a favoritos`)
      }
      console.log('Favoritos actuales:', favorites.value)
    } catch (error) {
      console.error('Error al modificar favoritos:', error)
    }
  };

  onMounted(async () => {
    await fetchSites()
    await fetchFavorites()
  })
</script>

<template>
  <div class="mb-8">
    <div class="flex flex-row justify-between items-center mb-4">
        <h2 class="text-2xl sm:text-4xl text-proyecto-primary font-semibold">{{ title }}</h2>
        <a href="#" class="text-sm sm:text-md font-semibold hover:bg-proyecto-primary hover:text-white rounded-full px-2.5 sm:px-4 py-1 sm:py-2 transition-colors duration-400">Ver Todos <i class="fa-solid fa-chevron-right ml-1"></i></a>
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
            :is-authenticated="authStore.isAuthenticated"
            @toggle-favorite="toggleFavorite"
        ></Card>
      </li>
    </ul>
    <div v-else class="h-[200px] flex justify-center items-center">
      <p class="px-5 py-2 text-white bg-proyecto-primary/80 text-center rounded-full inline-flex font-semibold shadow-md select-none"> No hay Contenido</p>
    </div>
  </div>
</template>
