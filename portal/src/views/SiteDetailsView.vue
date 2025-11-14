<template>
  <div class="flex flex-col items-center justify-center max-w-[1200px] w-full">
    <section class="w-full p-3 max-w-screen-xl">
      <ButtonPrimary :text="'Volver'" :icon_left="'fa-solid fa-arrow-left mr-2'" :link="'/sites'" :class="'my-4'"/>

      <div class="flex items-start gap-4 w-full pt-1 pb-3 flex-wrap relative">
        <!-- (image + aside unchanged) -->
        <!-- ... existing image carousel and aside ... -->
        <div class="flex flex-col flex-1 min-w-[300px]">
          <!-- image area -->
          <div class="relative h-[400px] w-full overflow-hidden rounded-lg">
            <img
              v-if="currentImage"
              :src="currentImage.url"
              :alt="currentImage.title || 'Site image'"
              class="absolute inset-0 w-full h-full object-cover"
            />
            <div v-else class="absolute inset-0 bg-gray-200 animate-pulse" />
            <button v-if="hasImages" type="button" @click="prev" class="absolute top-0 left-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none">
              <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 group-hover:bg-white/50 group-focus:ring-4 group-focus:ring-white">
                <svg class="w-4 h-4 text-white rtl:rotate-180" fill="none" viewBox="0 0 6 10">
                  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 1 1 5l4 4"/>
                </svg>
              </span>
            </button>
            <button v-if="hasImages" type="button" @click="next" class="absolute top-0 right-0 z-30 flex items-center justify-center h-full px-4 cursor-pointer group focus:outline-none">
              <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/30 group-hover:bg-white/50 group-focus:ring-4 group-focus:ring-white">
                <svg class="w-4 h-4 text-white rtl:rotate-180" fill="none" viewBox="0 0 6 10">
                  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 9 4-4-4-4"/>
                </svg>
              </span>
            </button>
          </div>
          <div v-if="hasImages" class="mt-4 flex flex-row gap-2 flex-wrap">
            <button
              v-for="(img, idx) in images"
              :key="img.id || idx"
              @click="setActive(idx)"
              class="w-24 h-16 overflow-hidden rounded border cursor-pointer focus:outline-none"
              :class="idx === activeIndex ? 'ring-2 ring-proyecto-accent' : 'hover:ring-2 hover:ring-gray-300'"
            >
              <img :src="img.url" :alt="img.title || 'Thumbnail'" class="w-full h-full object-cover">
            </button>
          </div>
        </div>

        <aside class="flex gap-4 flex-col max-w-[300px]">
          <div class="flex justify-between items-start gap-2 relative">
            <h2 class="text-2xl font-bold">
              {{ detalle.name || 'Cargando...' }}
            </h2>
            <button
              v-if="isAuthenticated && detalle.id"
              @click="toggleFavorite"
              data-tooltip-target="tooltip-favorite"
              class="flex items-center justify-center bg-gray-100/60 p-2 rounded-full hover:text-red-500 hover:fill-red-500 hover:ring-2 hover:ring-red-500 transition"
              :class="{ 'text-red-500 fill-red-500 ring-2 ring-red-500': isFavorite }"
            >
              <IconFavorite class="h-5" />
            </button>
          </div>
          <div id="tooltip-favorite" role="tooltip" class="absolute z-10 invisible inline-block px-3 py-2 text-sm font-medium text-red-500 transition-opacity duration-300 bg-gray-50 rounded-lg shadow-md opacity-0 tooltip">
            {{ isFavorite ? 'Quitar de Favoritos' : 'Agregar a favoritos' }}
            <div class="tooltip-arrow" data-popper-arrow></div>
          </div>
          <div class="flex gap-1 items-center border-b-2 pb-2">
            <Stars :rating="detalle.average_rating || 0" :class="'w-32'"/>
            <span class="text-lg font-semibold text-yellow-500">
              ({{ detalle.review_count || 0 }})
            </span>
          </div>
          <div class="flex gap-2 border-b-2 pt-1 pb-2" v-if="detalle.province || detalle.city">
            <IconLocation class="fill-red-700 w-4"/>
            <div>
              <span class="font-semibold text-gray-500">{{ detalle.province }}, </span>
              <span class="font-semibold text-gray-500">{{ detalle.city }}</span>
            </div>
          </div>
          <div class="flex gap-7">
            <div>
              <p class="font-semibold">Estado de conservación</p>
              <span>{{ detalle.state_of_conservation || '-' }}</span>
              <p class="font-semibold">Año de inauguración</p>
              <span>{{ detalle.inauguration_year || '-' }}</span>
            </div>
            <div>
              <p class="font-semibold">Categoria</p>
              <span>{{ detalle.category || '-' }}</span>
              <p class="font-semibold">Subido</p>
              <span>{{ detalle.inserted_at || '-' }}</span>
            </div>
          </div>
          <div class="flex justify-between gap-2">
            <ButtonPrimary :text="'Ver en el mapa'" :icon_left="'fa-solid fa-arrow-down mr-2'" @click="scrollToMap"/>
            <ButtonPrimary :text="'Reseñas'" :icon_left="'fa-solid fa-arrow-down mr-2'" @click="scrollToReviews"/>
          </div>
        </aside>
      </div>

      <!-- Brief description standalone -->
      <div v-if="shortDescription" class="mt-6 w-full bg-white rounded-xl p-5 shadow">
        <h3 class="text-xl font-semibold mb-2 text-proyecto-accent">Descripción breve del sitio</h3>
        <p class="text-gray-700 whitespace-pre-line">{{ shortDescription }}</p>
      </div>

      <!-- Detailed description accordion full width -->
      <div class="mt-6 w-full">
        <Acordion :content="detailedContent"/>
      </div>
    </section>

    <div class="w-full max-w-[1200px] flex flex-col gap-3 mt-3">
      <h3 class="text-3xl text-proyecto-accent">Locación</h3>
      <div id="map" class="w-full">
        <MapDetail
          v-if="hasLocation"
          :mark="[Number(detalle.lat), Number(detalle.lon)]"
          :markName="detalle.name"
          :zoom="14"
        />
        <p v-else class="text-sm text-gray-500">Sin coordenadas para mostrar el mapa.</p>
      </div>
    </div>

    <section id="reviews" class="w-full max-w-[1200px] flex flex-col gap-3 mt-3">
      <h3 class="text-3xl text-proyecto-accent">Reseñas</h3>
      <ButtonPrimary :text="'Dar reseña'" :icon_left="'fa-solid fa-plus mr-2'" class="max-w-36 w-auto"/>
      <Review
        v-for="r in reviews"
        :key="r.id"
        :user_name="r.user_name"
        :user_email="r.user_email"
        :text="r.comment"
        :created_at="r.inserted_at"
        :rating="r.rating"
      />
      <p
        v-if="canLoadMore"
        @click="fetchReviews"
        class="text-proyecto-primary font-semibold cursor-pointer hover:text-proyecto-accent transition-all ease-in-out"
      >
        Ver más reseñas...
      </p>
      <SkeletonReview v-if="reviews.length == 0 && page == 1" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import Stars from '@/components/Stars.vue'
import IconLocation from '@/components/icons/IconLocation.vue'
import IconFavorite from '@/components/icons/IconFavorite.vue'
import Acordion from '@/components/Acordion.vue'
import api from '@/api/axios'
import Review from '@/components/Review.vue'
import ButtonPrimary from '@/components/buttons/ButtonPrimary.vue'
import { useAuthStore } from '@/stores/auth.js'
import { useFavoritesStore } from '@/stores/favorites.js'
import MapDetail from '@/components/MapDetail.vue'
import SkeletonReview from '@/components/SkeletonReview.vue'

const route = useRoute()
const detalle = ref({})
const detailedContent = ref([])
const shortDescription = ref('')
const reviews = ref([])
const page = ref(1)
const activeIndex = ref(0)

const authStore = useAuthStore()
const favoritesStore = useFavoritesStore()
const { isAuthenticated } = storeToRefs(authStore)

const images = computed(() => detalle.value.images || [])
const currentImage = computed(() => images.value[activeIndex.value] || null)
const hasImages = computed(() => images.value.length > 0)
const isFavorite = computed(() => detalle.value.id ? favoritesStore.isFavorite(detalle.value.id) : false)

const hasLocation = computed(() =>
  detalle.value &&
  detalle.value.lat !== null &&
  detalle.value.lon !== null &&
  detalle.value.lat !== undefined &&
  detalle.value.lon !== undefined &&
  !Number.isNaN(Number(detalle.value.lat)) &&
  !Number.isNaN(Number(detalle.value.lon))
)

const canLoadMore = computed(() => reviews.value.length && reviews.value.length % 10 === 0)

const fetchDetalleSitio = async () => {
  try {
    const { data } = await api.get(`${route.path}`)
    const formattedDate = data.inserted_at
      ? data.inserted_at.slice(0, data.inserted_at.indexOf('T')).replaceAll('-', '/')
      : null
    detalle.value = { ...data, inserted_at: formattedDate }
    shortDescription.value = data.short_description || '-'
    detailedContent.value = [
      { id: 1, header: 'Descripción detallada', text: data.description || '-' }
    ]
  } catch (error) {
    console.error('Error al cargar detalle:', error)
  }
}

const fetchReviews = async () => {
  try {
    const resp = await api.get(`${route.path}/reviews`, { params: { page: page.value } })
    reviews.value = [...reviews.value, ...(resp.data.data || [])]
    page.value++
  } catch (error) {
    console.error('Error al cargar reseñas:', error)
  }
}

const toggleFavorite = async () => {
  if (!detalle.value.id) return
  try {
    await favoritesStore.toggleFavorite(detalle.value.id)
  } catch (error) {
    console.error('Error al modificar favoritos:', error)
  }
}

watch(images, (arr) => {
  if (arr && arr.length) {
    const coverIdx = arr.findIndex(i => i.is_cover)
    activeIndex.value = coverIdx >= 0 ? coverIdx : 0
  } else {
    activeIndex.value = 0
  }
}, { immediate: true })

const prev = () => {
  if (!hasImages.value) return
  activeIndex.value = (activeIndex.value - 1 + images.value.length) % images.value.length
}

const next = () => {
  if (!hasImages.value) return
  activeIndex.value = (activeIndex.value + 1) % images.value.length
}

const setActive = (idx) => { activeIndex.value = idx }

onMounted(async () => {
  await fetchDetalleSitio()
  await fetchReviews()
  if (isAuthenticated.value) {
    await favoritesStore.fetchFavorites()
  }
})

const scrollToMap = () => {
  document.getElementById('map')?.scrollIntoView({ behavior: 'smooth' })
}
const scrollToReviews = () => {
  document.getElementById('reviews')?.scrollIntoView({ behavior: 'smooth' })
}
</script>
