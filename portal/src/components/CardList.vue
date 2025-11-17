<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue';
import Card from '@/components/Card.vue';

const props = defineProps({
  sites: { type: Array, required: true, default: () => [] },
  isAuthenticated: { type: Boolean, required: true },
  isFavorite: { type: Function, required: true },
  toggleFavorite: { type: Function, required: false },
  hideFavoriteButton: { type: Boolean, required: false, default: false }
});

// Detectar el tamaño de pantalla
const screenSize = ref('xl');

const updateScreenSize = () => {
  const width = window.innerWidth;
  if (width < 768) screenSize.value = 'sm';
  else if (width < 1024) screenSize.value = 'md';
  else if (width < 1280) screenSize.value = 'lg';
  else screenSize.value = 'xl';
};

onMounted(() => {
  updateScreenSize();
  window.addEventListener('resize', updateScreenSize);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenSize);
});

// Determinar si usar scroll horizontal
const useScroll = computed(() => {
  return screenSize.value === 'sm' || screenSize.value === 'md';
});

// Número de cards por slide según el breakpoint
const cardsPerSlide = computed(() => {
  switch (screenSize.value) {
    case 'sm': return 2;
    case 'md': return 3;
    case 'lg': return 4;
    default: return 5;
  }
});

// Dividir sitios según el número de cards por slide
const splittedSites = computed(() => {
  const perSlide = cardsPerSlide.value;
  const result = [];
  for (let i = 0; i < props.sites.length; i += perSlide) {
    result.push(props.sites.slice(i, i + perSlide));
  }
  return result;
});

const currentSlide = ref(0);
const direction = ref('next');

function prev() {
  if (currentSlide.value > 0) {
    direction.value = 'prev';
    currentSlide.value--;
  }
}

function next() {
  if (currentSlide.value < splittedSites.value.length - 1) {
    direction.value = 'next';
    currentSlide.value++;
  }
}

// Reset slide cuando cambia el tamaño de pantalla
const prevCardsPerSlide = ref(cardsPerSlide.value);
const checkSlideReset = () => {
  if (prevCardsPerSlide.value !== cardsPerSlide.value) {
    currentSlide.value = 0;
    prevCardsPerSlide.value = cardsPerSlide.value;
  }
};

// Ejecutar check cuando cambie cardsPerSlide
const unwatchCardsPerSlide = computed(() => {
  checkSlideReset();
  return cardsPerSlide.value;
});
</script>

<template>
  <div v-if="props.sites.length" class="relative w-full mt-4">
    <!-- Scroll horizontal para sm y md -->
    <div v-if="useScroll" class="overflow-x-auto pb-4 scrollbar-hide">
      <ul class="flex gap-4 px-2">
        <li
          v-for="site in props.sites"
          :key="site.id"
          class="flex-none w-40 sm:w-48 md:w-56"
        >
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
            :created_at="site.inserted_at"
          />
        </li>
      </ul>
    </div>

    <!-- Carousel con flechas para lg y xl -->
    <div v-else class="relative lg:h-[500px]">
      <div
        v-for="(group, idx) in splittedSites"
        :key="idx"
        class="duration-700 ease-in-out"
        v-show="idx === currentSlide"
      >
        <ul class="flex pb-4 lg:px-2 justify-center gap-4 xl:justify-evenly">
          <li
            v-for="site in group"
            :key="site.id"
            class="flex-none w-64"
          >
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
              :created_at="site.inserted_at"
            />
          </li>
        </ul>
      </div>

      <!-- Controls -->
      <button
        type="button"
        class="absolute top-0 -left-2 xl:-left-16 z-30 flex items-center justify-center h-full px-4 disabled:opacity-30"
        @click="prev"
        :disabled="currentSlide === 0"
      >
        <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white shadow-lg">
          <i class="fa-solid fa-arrow-left text-proyecto-primary"></i>
          <span class="sr-only">Prev</span>
        </span>
      </button>
      <button
        type="button"
        class="absolute top-0 -right-2 xl:-right-16 z-30 flex items-center justify-center h-full px-4 disabled:opacity-30"
        @click="next"
        :disabled="currentSlide === splittedSites.length - 1"
      >
        <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 shadow-lg">
          <i class="fa-solid fa-arrow-right text-proyecto-primary"></i>
          <span class="sr-only">Next</span>
        </span>
      </button>
    </div>
  </div>

  <div v-else class="h-[200px] flex justify-center items-center">
    <p class="px-5 py-2 text-white bg-proyecto-primary/80 rounded-full font-semibold">No hay Contenido</p>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
