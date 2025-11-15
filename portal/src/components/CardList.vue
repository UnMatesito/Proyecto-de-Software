<script setup lang="ts">
import { computed, ref } from 'vue';
import Card from '@/components/Card.vue';

const props = defineProps({
  sites: { type: Array, required: true, default: () => [] },
  isAuthenticated: { type: Boolean, required: true },
  isFavorite: { type: Function, required: true },
  toggleFavorite: { type: Function, required: false },
  hideFavoriteButton: { type: Boolean, required: false, default: false }
});

// Split sites into two halves
const splittedSites = computed(() => {
  const mid = Math.ceil(props.sites.length / 2);
  return [props.sites.slice(0, mid), props.sites.slice(mid)];
});

// Active slide (0 or 1)
const currentSlide = ref(0);

function prev() {
  if (currentSlide.value > 0) currentSlide.value--;
}

function next() {
  if (currentSlide.value < splittedSites.value.length - 1) currentSlide.value++;
}
</script>

<template>
  <div v-if="props.sites.length" class="relative w-full mt-4">
    <div class="relative h-[500px]">
      <div
        v-for="(group, idx) in splittedSites"
        :key="idx"
        class="duration-700 ease-in-out"
        v-show="idx === currentSlide"
      >
        <ul class="flex gap-3 sm:gap-4 pb-4 lg:px-2 justify-evenly">
          <li
            v-for="site in group"
            :key="site.id"
            class="flex-none w-40 sm:w-48 md:w-56 lg:w-64"
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
            />
          </li>
        </ul>
      </div>
    </div>

    <!-- Controls -->
    <button
      type="button"
      class="absolute top-0 left-0 z-30 flex items-center justify-center h-full px-4 disabled:opacity-30"
      @click="prev"
      :disabled="currentSlide === 0"
    >
      <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 shadow-md">
        <i class="fa-solid fa-arrow-left text-proyecto-primary"></i>
        <span class="sr-only">Prev</span>
      </span>
    </button>
    <button
      type="button"
      class="absolute top-0 right-0 z-30 flex items-center justify-center h-full px-4 disabled:opacity-30"
      @click="next"
      :disabled="currentSlide === splittedSites.length - 1"
    >
      <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 shadow-md">
        <i class="fa-solid fa-arrow-right text-proyecto-primary"></i>
        <span class="sr-only">Next</span>
      </span>
    </button>
  </div>

  <div v-else class="h-[200px] flex justify-center items-center">
    <p class="px-5 py-2 text-white bg-proyecto-primary/80 rounded-full font-semibold">No hay Contenido</p>
  </div>
</template>
