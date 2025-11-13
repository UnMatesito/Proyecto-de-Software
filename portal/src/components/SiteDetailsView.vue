<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api/axios.js';
import IconLocation from '@/components/icons/IconLocation.vue';
import ButtonPrimary from '@/components/buttons/ButtonPrimary.vue';
import Stars from '@/components/Stars.vue';
import IconFavorite from '@/components/icons/IconFavorite.vue';

const route = useRoute();
const dataSite = ref({ images: [], tags: [] });
const activeIndex = ref(0);

const images = computed(() => dataSite.value.images || []);
const currentImage = computed(() => images.value[activeIndex.value] || null);
const hasImages = computed(() => images.value.length > 0);

const fetchSiteDetails = async (siteID) => {
  try {
    const response = await api.get(`/sites/${siteID}`);
    dataSite.value = response.data;
  } catch (error) {
    console.error('Error fetching site details:', error);
  }
};

onMounted(() => {
  const siteId = route.params.site_id;
  if (siteId) fetchSiteDetails(siteId);
});

// Select cover image if available
watch(images, (arr) => {
  if (arr && arr.length) {
    const coverIdx = arr.findIndex(i => i.is_cover);
    activeIndex.value = coverIdx >= 0 ? coverIdx : 0;
  } else {
    activeIndex.value = 0;
  }
}, { immediate: true });

const prev = () => {
  if (!hasImages.value) return;
  activeIndex.value = (activeIndex.value - 1 + images.value.length) % images.value.length;
};

const next = () => {
  if (!hasImages.value) return;
  activeIndex.value = (activeIndex.value + 1) % images.value.length;
};

const setActive = (idx) => { activeIndex.value = idx; };
</script>

<template>
  <div class="flex flex-row gap-4 p-4 w-screen min-h-screen bg-proyecto-secondary">
    <!-- Carusel de imagenes -->
    <div class="flex flex-col w-full">
      <!-- Imagen principal -->
      <div class="relative h-[80%] w-full overflow-hidden -m-4 mr-3">
        <img
          v-if="currentImage"
          :src="currentImage.url"
          :alt="currentImage.title || 'Site image'"
          class="absolute inset-0 w-full h-full object-cover"
        />
        <div v-else class="absolute inset-0 bg-gray-200 animate-pulse" />

        <!-- Prev button -->
        <button
          type="button"
          @click="prev"
          class="absolute top-0 left-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none"
        >
          <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 group-hover:bg-white/50 group-focus:ring-4 group-focus:ring-white">
            <svg class="w-4 h-4 text-white rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 6 10">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 1 1 5l4 4"/>
            </svg>
            <span class="sr-only">Previous</span>
          </span>
        </button>

        <!-- Next button -->
        <button
          type="button"
          @click="next"
          class="absolute top-0 right-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none"
        >
          <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 group-hover:bg-white/50 group-focus:ring-4 group-focus:ring-white">
            <svg class="w-4 h-4 text-white rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 6 10">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
            </svg>
            <span class="sr-only">Next</span>
          </span>
        </button>
      </div>

      <!-- Thumbnails -->
      <div v-if="hasImages" class="mt-8 flex flex-row gap-2 flex-wrap">
        <button
          v-for="(img, idx) in images"
          :key="img.id || idx"
          @click="setActive(idx)"
          class="w-24 h-16 overflow-hidden rounded border cursor-pointer focus:outline-none"
          :class="idx === activeIndex ? 'ring-2 ring-proyecto-accent' : 'hover:ring-2 hover:ring-gray-300'"
        >
          <img :src="img.url" :alt="img.title || 'Thumbnail'" class="w-full h-full object-fill">
        </button>
      </div>
      <p v-else class="mt-3 text-gray-500 italic">No hay imagenes disponibles</p>
    </div>

    <!-- Detalles del sitio y reviews -->
    <div class="h-full w-full pt-10">
      <div class="flex flex-row justify-between items-center mb-4">
        <div class="flex flex-row items-center gap-2.5 text-xl">
          <IconLocation class="h-5 fill-proyecto-primary" />
          <p>{{ dataSite.city }}, {{ dataSite.province }}</p>
        </div>
        <button class="flex-row flex items-center gap-x-2 bg-gray-100/60 px-2 py-1 rounded-full mr-5 hover:text-red-500 hover:fill-red-500 hover:ring-2 hover:ring-red-500 transition">
          <IconFavorite class="h-5" />Agregar a Favoritos
        </button>
      </div>

      <h1 class="font-bold text-7xl">{{ dataSite.name }}</h1>
      <p class="mt-4 text-lg">{{ dataSite.description }}</p>
      <p class="mt-4"><span class="font-semibold">Estado de conservacion:</span> {{ dataSite.state_of_conservation }}</p>
      <p class="mt-4"><span class="font-semibold">Categoria:</span> {{ dataSite.category }}</p>

      <div class="space-x-2 mt-4" v-if="dataSite.tags && dataSite.tags.length">
        <span v-for="tag in dataSite.tags" :key="tag" class="px-3 py-1 rounded-full bg-blue-100 text-sm border-2 border-blue-600 text-blue-600 capitalize font-semibold">{{ tag }}</span>
      </div>
      <p v-else class="text-gray-500 italic mt-4">No hay Tags para mostrar</p>

      <!-- Reviews -->
      <div>
        <h2 class="font-bold text-3xl mt-10 mb-4">Reseñas del sitio</h2>
        <div class="w-full bg-gray-100 h-full px-6 py-10 rounded-lg flex flex-row items-center justify-center shadow-md">
          <div>
            <img src="https://i.pravatar.cc/40" alt="User Avatar" class="w-10 h-10 rounded-full mr-4" />
          </div>
          <form action="" method="POST" class="flex flex-col gap-4 w-full">
            <div class="flex flex-row gap-4 items-center">
              <input type="text" placeholder="Escribe tu reseña..." class="w-full h-12 px-4 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-proyecto-accent" />
              <Stars class="w-[20%]" />
            </div>
            <ButtonPrimary text="Enviar" type="submit" class="font-semibold" />
          </form>
        </div>

        <div v-for="review in [1,2,3]" :key="review" class="w-full bg-white mt-4 px-6 py-4 rounded-lg flex flex-row items-center shadow-md">
          <div class="flex flex-row items-center">
            <img src="https://i.pravatar.cc/40" alt="User Avatar" class="w-10 h-10 rounded-full mr-4" />
            <div class="flex flex-col gap-y-2">
              <p>Lorem ipsum dolor sit amet...</p>
              <Stars />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
