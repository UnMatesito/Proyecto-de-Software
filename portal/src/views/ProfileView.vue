<template>
  <div class="container mx-auto max-w-4xl px-4 py-8">
    <h1 class="mb-6 text-3xl font-bold text-gray-800">Mi Perfil</h1>

    <div v-if="user" class="mb-8 flex items-center space-x-4 rounded-lg bg-white p-6 shadow-md">
      <img
        :src="user.avatar || 'https://via.placeholder.com/150'"
        alt="Avatar"
        class="h-20 w-20 rounded-full border-2 border-gray-300 object-cover"
        referrerpolicy="no-referrer"
      >
      <div>
        <h2 class="text-2xl font-semibold text-gray-700">{{ user.name }}</h2>
        <p class="text-gray-500">{{ user.email }}</p>
      </div>
    </div>
    <div v-else class="mb-8 rounded-lg bg-white p-6 text-center text-gray-500 shadow-md">
      Cargando información del usuario...
    </div>

    <div class="mb-4 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          @click="activeTab = 'reviews'"
          :class="[
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium',
            activeTab === 'reviews'
              ? 'border-proyecto-primary text-proyecto-primary'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
          ]"
        >
          Mis Reseñas
        </button>
        <button
          @click="activeTab = 'favorites'"
          :class="[
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium',
            activeTab === 'favorites'
              ? 'border-proyecto-primary text-proyecto-primary'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
          ]"
        >
          Mis Sitios Favoritos
        </button>
      </nav>
    </div>

    <div>
      <div v-if="loading" class="py-10 text-center">
        <p class="text-gray-500">Cargando...</p>
      </div>

      <div v-else>
        <section v-show="activeTab === 'reviews'">
          <h3 class="mb-4 text-xl font-semibold text-gray-700">Mis Reseñas</h3>

          <div class="mb-4 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div class="flex items-center gap-2">
              <label for="reviews-sort" class="text-sm font-medium text-gray-700">Ordenar por</label>
              <select
                id="reviews-sort"
                v-model="reviewsSortOrder"
                class="rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-proyecto-primary focus:outline-none"
                @change="handleReviewSortChange"
              >
                <option value="date_desc">Más Recientes</option>
                <option value="date_asc">Más Antiguos</option>
              </select>
            </div>
          </div>

          <div v-if="reviewsLoading" class="py-5 text-center">Cargando reseñas...</div>

          <div v-else>
            <div v-if="reviews.length > 0" class="space-y-4">
              <article
                v-for="review in reviews"
                :key="review.id"
                class="rounded-lg bg-white p-4 shadow"
              >
                <p class="text-sm text-gray-500">{{ new Date(review.inserted_at).toLocaleDateString() }}</p>
                <h4 class="mt-1 text-lg font-semibold text-gray-800">{{ review.site.name }}</h4>
                <div class="mt-2 flex items-center gap-2">
                  <span class="font-semibold text-gray-700">Calificación:</span>
                  <RatingStars :rating="review.rating" />
                </div>
                <p class="mt-3 text-gray-600">{{ review.comment }}</p>
              </article>
            </div>
            <p v-else class="text-gray-500 italic">Aún no escribiste reseñas.</p>

            <div class="mt-6">
              <Pagination
                :page="reviewsPage"
                :total-pages="reviewsTotalPages"
                :page-size="reviewsPerPage"
                :page-size-options="reviewPageSizeOptions"
                @page-change="handleReviewPageChange"
                @page-size-change="handleReviewPageSizeChange"
              />
            </div>
          </div>
        </section>

        <section v-show="activeTab === 'favorites'">
          <h3 class="mb-4 text-xl font-semibold text-gray-700">Mis Sitios Favoritos</h3>

          <div v-if="favoritesLoading" class="py-5 text-center">Cargando favoritos...</div>

          <div v-else>
            <div v-if="favorites.length > 0" class="space-y-4">
              <article
                v-for="fav in favorites"
                :key="fav.site_id"
                class="flex items-center justify-between rounded-lg bg-white p-4 shadow"
              >
                <div>
                  <p class="font-medium text-gray-800">{{ fav.name }}</p>
                  <p class="text-sm text-gray-500">{{ fav.city }}</p>
                </div>
                <a :href="`/sites/${fav.site_id}`" class="text-sm text-proyecto-primary hover:underline">Ver sitio</a>
              </article>
            </div>
            <p v-else class="text-gray-500 italic">Aún no marcaste ningún sitio como favorito.</p>

            <div v-if="favorites.length > 0 && favoritesTotalPages > 1" class="mt-6">
              <Pagination
                :page="favoritesPage"
                :total-pages="favoritesTotalPages"
                @page-change="handleFavoritePageChange"
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import Pagination from '@/components/Pagination.vue';
import RatingStars from '@/components/Stars.vue';
import api from '../api/axios.js';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const user = authStore.user;

const activeTab = ref('reviews');

const reviews = ref([]);
const reviewsPage = ref(1);
const reviewsTotalPages = ref(1);
const reviewsPerPage = ref(25);
const reviewsLoading = ref(true);
const reviewsSortOrder = ref('date_desc');
const reviewPageSizeOptions = Object.freeze([25, 50, 100]);

const favorites = ref([]);
const favoritesPage = ref(1);
const favoritesTotalPages = ref(1);
const favoritesLoading = ref(true);

const loading = computed(() => reviewsLoading.value && favoritesLoading.value);

async function fetchReviews(page = 1) {
  reviewsLoading.value = true;

  try {
    const response = await api.get('/me/reviews', {
      params: {
        page,
        per_page: reviewsPerPage.value,
        sort: reviewsSortOrder.value,
      },
    });

    reviews.value = response.data?.data ?? [];
    reviewsPage.value = response.data?.meta?.page ?? page;
    reviewsTotalPages.value =
      response.data?.meta?.total_pages ?? 1;
  } catch (error) {
    console.error('Error al cargar reseñas:', error);
    reviews.value = [];
    reviewsPage.value = 1;
    reviewsTotalPages.value = 1;
  } finally {
    reviewsLoading.value = false;
  }
}

async function fetchFavorites(page = 1) {
  favoritesLoading.value = true;

  try {
    const response = await api.get('/me/favorites', {
      params: {
        page,
      },
    });

    favorites.value = response.data?.data ?? [];
    favoritesPage.value = response.data?.meta?.page ?? page;
    favoritesTotalPages.value =
      response.data?.meta?.total_pages ?? 1;
  } catch (error) {
    console.error('Error al cargar favoritos:', error);
    favorites.value = [];
    favoritesPage.value = 1;
    favoritesTotalPages.value = 1;
  } finally {
    favoritesLoading.value = false;
  }
}

onMounted(() => {
  fetchReviews(1);
  fetchFavorites(1);
});

function handleReviewPageChange(newPage) {
  fetchReviews(newPage);
}

function handleReviewPageSizeChange(newSize) {
  if (reviewsPerPage.value === newSize) {
    return;
  }
  reviewsPerPage.value = newSize;
  fetchReviews(1);
}

function handleReviewSortChange() {
  fetchReviews(1);
}

function handleFavoritePageChange(newPage) {
  fetchFavorites(newPage);
}
</script>
