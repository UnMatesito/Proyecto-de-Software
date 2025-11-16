<template>
  <div class="flex flex-col items-center justify-center max-w-[1200px] w-full">
    <section class="w-full p-3 max-w-screen-xl">
      <ButtonPrimary :text="'Volver'" :icon_left="'fa-solid fa-arrow-left mr-2'" :link="prevURL || '/sites'" :class="'my-4'"/>
      <div class="flex items-start gap-4 w-full pt-1 pb-3 flex-wrap relative justify-center">
        <!-- (image + aside unchanged) -->
        <!-- ... existing image carousel and aside ... -->
        <div class="flex flex-col flex-1 min-w-[300px]">
          <!-- image area -->
          <div class="relative h-[400px] w-full overflow-hidden rounded-lg">
            <div v-if="currentImage">
              <img
                :src="currentImage.url"
                :alt="currentImage.title || 'Site image'"
                class="absolute inset-0 w-full h-full object-cover"
              />
              <p class="absolute bottom-0 text-white bg-proyecto-primary px-5 py-1 rounded-r-md opacity-70 font-semibold">{{ currentImage.title }}</p>
            </div>
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

        <aside class="flex gap-4 flex-col sm:max-w-[300px] w-full">
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
          <div class="flex gap-1 sm:gap-2 text-blue-700 flex-wrap border-t-2 pt-1 sm:pt-2 pb-0.5 sm:pb-1">
            <span v-for="tag in detalle.tags" :key="tag" class="inline-flex items-center bg-blue-50 text-blue-500 text-[10px] sm:text-xs font-semibold px-1.5 sm:px-2.5 py-0.5 border sm:border-2 rounded-full border-blue-500 whitespace-nowrap">{{ tag }}</span>
          </div>
          <div class="flex justify-between gap-2 flex-wrap">
            <ButtonPrimary :text="'Ver en el mapa'" id="scroll_to_map" class="justify-center" :icon_left="'fa-solid fa-arrow-down mr-2'" @click="scrollToMap"/>
            <ButtonPrimary :text="'Reseñas'" id="scroll_to_reviews"class="justify-center" :icon_left="'fa-solid fa-arrow-down mr-2'" @click="scrollToReviews"/>
          </div>
        </aside>
      </div>

      <!-- DESCRIPCIÓN BREVE -->
      <div v-if="shortDescription" class="mt-6 w-full bg-white rounded-xl p-5 shadow">
        <h3 class="text-xl font-semibold mb-2 text-proyecto-accent">Descripción breve del sitio</h3>
        <p class="text-gray-700 whitespace-pre-line">{{ shortDescription }}</p>
      </div>

      <!-- DETALLE COMPLETO -->
      <div class="mt-6 w-full">
        <Acordion :content="detailedContent"/>
      </div>
    </section>

    <div class="w-full max-w-[1200px] flex flex-col gap-3 mt-3 p-3">
      <h3 id="map_title" class="text-3xl text-proyecto-accent mx-2">Ubicación</h3>
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

    <!-- SI reviewsEnabled ES TRUE mostrar reseñas-->
    <section v-if="reviewsEnabled" class="w-full max-w-[1200px] flex flex-col gap-3 mt-3">
      <!-- Listado -->
      <section id="reviews" class="w-full max-w-[1200px] flex flex-col gap-3 mt-3 mb-2">

        <div class="flex flex-row justify-between items-center mx-2 flex-wrap gap-2">
          <h3 class="text-3xl text-proyecto-accent">Reseñas</h3>

          <ButtonPrimary
            v-if="!isAuthenticated"
            :text="'Iniciar sesión para dejar una reseña'"
            :icon_left="'fa-solid fa-right-to-bracket mr-2'"
            class="w-auto"
            @click="loginWithGoogle"
          />
          <ButtonPrimary
            v-else
            :text="'Dejar reseña'"
            :icon_left="'fa-solid fa-plus mr-2'"
            class="w-auto"
            @click="goToReview"
          />
        </div>

        <Review
          v-for="r in reviews"
          :key="r.id"
          :user_name="r.user_name"
          :user_email="r.user_email"
          :text="r.comment"
          :created_at="r.inserted_at"
          :rating="r.rating"
        />

        <Pagination 
          class="p-3"
          :page="reviewsPage"
          :total-pages="reviewsTotalPages"
          :page-size="reviewsPerPage"
          :page-size-options="[10, 25, 50]"
          @page-change="handlePageChange"
          @page-size-change="handlePageSizeChange"
        />
      </section>
    </section>

    <!-- SI reviewsEnabled ES FALSE mostrar mensaje alternativo-->
    <section
      v-else
      id="reviews"
      class="w-full max-w-[1200px] flex flex-col gap-3 mt-3"
    >
      <h3 class="text-3xl text-proyecto-accent">Reseñas</h3>
      <p class="text-gray-600 text-sm">
        Las reseñas están deshabilitadas temporalmente.
      </p>
    </section>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
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
import Pagination from "@/components/Pagination.vue"


const prevURL = ref('')
const route = useRoute()
const router = useRouter()
const detalle = ref({})
const detailedContent = ref([])
const shortDescription = ref('')
const reviews = ref([])
const page = ref(1)
const activeIndex = ref(0)

const reviewsPage = ref(1)
const reviewsPerPage = ref(10)
const reviewsTotal = ref(0)
const reviewsTotalPages = computed(() =>
  Math.ceil(reviewsTotal.value / reviewsPerPage.value)
)
const reviewsLoading = ref(false)

const reviewsEnabled = ref(false)

prevURL.value = localStorage.prevURL || '/sites'
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

const reviewButtonLink = computed(() => {
  if (authStore.isAuthenticated) {
    return `/sites/${detalle.value.id}/review`
  }
  return "/login"
})


const fetchDetalleSitio = async () => {
  try {
    const { data } = await api.get(`${route.path}`)
    const formattedDate = data.inserted_at
    ? new Date(data.inserted_at).toLocaleDateString('es-AR')
    : '-'
    detalle.value = { ...data, inserted_at: formattedDate }
    shortDescription.value = data.short_description || '-'
    detailedContent.value = [
      { id: 1, header: 'Descripción detallada', text: data.description || '-' }
    ]
  } catch (error) {
    console.error('Error al cargar detalle:', error)
  }
}

const fetchReviews = async (page = 1) => {
  reviewsLoading.value = true

  try {
    const resp = await api.get(`${route.path}/reviews`, {
      params: {
        page,
        per_page: reviewsPerPage.value
      }
    })

    reviews.value = resp.data.data
    reviewsPage.value = resp.data.meta.page
    reviewsTotal.value = resp.data.meta.total

  } catch (error) {
    console.error("Error al cargar reseñas:", error)
  } finally {
    reviewsLoading.value = false
  }
}

function loginWithGoogle() {
  const currentPath = router.currentRoute.value.fullPath
  const apiUrl = import.meta.env.VITE_API_URL || "https://admin-grupo09.proyecto2025.linti.unlp.edu.ar/api"

  window.location.href = `${apiUrl}/auth/google/login?next=${encodeURIComponent(currentPath)}`
}

function goToReview() {
  router.push(`/sites/${detalle.value.id}/review`)
}

const fetchFeatureFlags = async () => {
  try {
    const { data } = await api.get("/feature-flags/reviews_enabled")
    reviewsEnabled.value = data.is_enabled
  } catch (error) {
    console.error("Error cargando feature flags:", error)
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

watch(images, () => {
  activeIndex.value = 0
}, { immediate: true })

const handlePageChange = (newPage) => {
  fetchReviews(newPage)
}

const handlePageSizeChange = (newSize) => {
  reviewsPerPage.value = newSize
  fetchReviews(1)
}


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
  await fetchFeatureFlags()
  if (reviewsEnabled.value) {
    await fetchReviews()
  }
  if (isAuthenticated.value) {
    await favoritesStore.fetchFavorites()
  }
})

const scrollToMap = () => {
  document.getElementById('map_title')?.scrollIntoView({ behavior: 'smooth' })
}
const scrollToReviews = () => {
  document.getElementById('reviews')?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style>
  #map_title {
    scroll-margin-top: 80px; /* ajustá a la altura de tu navbar para que el scroll se exacto */
  }

  #reviews {
    scroll-margin-top: 80px; /* ajustá a la altura de tu navbar para que el scroll se exacto */
  }

  @media (max-width: 600px) {
    #scroll_to_reviews, #scroll_to_map {
      width: 100%;
    }
  }

</style>