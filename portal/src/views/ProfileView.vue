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
        <!-- REVIEWS TAB -->
        <section v-show="activeTab === 'reviews'">
          <div
          v-if="showToast"
          class="fixed bottom-5 right-5 z-50 rounded-lg bg-green-600 px-4 py-3 text-white shadow-lg transition-all">
          {{ toastMessage }}
          </div>

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
                <p class="text-sm text-gray-500">
                  {{ new Date(review.inserted_at || review.created_at).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit', year: 'numeric' }) }}
                </p>
                <h4 class="mt-1 text-lg font-semibold text-gray-800">
                  {{ review.site?.name || review.name }}
                </h4>
                <div class="mt-2 flex items-center gap-2">
                  <span class="font-semibold text-gray-700">Calificación:</span>
                  <RatingStars :rating="review.rating" />
                </div>
                <p class="mt-3 text-gray-600">{{ review.comment || review.comment_excerpt }}</p>
                <!-- Estado -->
                <div class="mt-3">
                  <span
                    class="inline-flex items-center gap-1 rounded-xl px-3 py-1 text-sm font-semibold shadow-sm"
                    :class="{
                      'bg-yellow-100 text-yellow-800 border border-yellow-300': review.status === 'Pendiente',
                      'bg-green-100 text-green-800 border border-green-300': review.status === 'Aprobada',
                      'bg-red-100 text-red-800 border border-red-300': review.status === 'Rechazada'
                    }"
                  >
                    <i class="fa-solid fa-circle text-[8px]"></i>
                    Estado: {{ review.status }}
                  </span>
                </div>
                <!-- Motivo del rechazo -->
                <div v-if="review.status === 'Rechazada'" class="mt-2 text-red-600 text-sm">
                  Motivo del rechazo: {{ review.rejected_reason || 'No especificado' }}
                </div>
                <div class="mt-3 flex justify-end">
                  <button
                    @click="deleteReview(review)"
                    class="text-red-600 text-sm hover:underline"
                  >
                    Eliminar
                  </button>
                </div>
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

        <!-- FAVORITES TAB -->
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
                <div class="flex items-center gap-3">
                  <a
                    :href="`/sites/${fav.site_id}`"
                    class="text-sm text-proyecto-primary hover:underline"
                  >
                    Ver sitio
                  </a>
                  <button
                    @click="removeFavorite(fav.site_id)"
                    class="rounded-lg bg-red-500 px-3 py-1.5 text-sm text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-300"
                  >
                    Quitar
                  </button>
                </div>
              </article>
            </div>
            <p v-else class="text-gray-500 italic">Aún no marcaste ningún sitio como favorito.</p>

            <div v-if="favorites.length > 0" class="mt-6">
              <Pagination
                :page="favoritesPage"
                :total-pages="favoritesTotalPages"
                :page-size="favoritesPerPage"
                :page-size-options="favoritePageSizeOptions"
                page-size-label="Sitios por página"
                @page-change="handleFavoritePageChange"
                @page-size-change="handleFavoritePageSizeChange"
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

const showToast = ref(false);
const toastMessage = ref("");


// Reviews state
const reviews = ref([]);
const reviewsPage = ref(1);
const reviewsTotalPages = ref(1);
const reviewsPerPage = ref(25);
const reviewsLoading = ref(true);
const reviewsSortOrder = ref('date_desc');
const reviewPageSizeOptions = Object.freeze([25, 50, 100]);

// Favorites state
const favorites = ref([]);
const favoritesPage = ref(1);
const favoritesTotalPages = ref(1);
const favoritesPerPage = ref(25);
const favoritesLoading = ref(true);
const favoritePageSizeOptions = Object.freeze([10, 25, 50]);

// Combined loading state
const loading = computed(() => reviewsLoading.value && favoritesLoading.value);

// Fetch reviews
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
    reviewsTotalPages.value = response.data?.meta?.total_pages ?? 1;
  } catch (error) {
    console.error('Error al cargar reseñas:', error);
    reviews.value = [];
    reviewsPage.value = 1;
    reviewsTotalPages.value = 1;
  } finally {
    reviewsLoading.value = false;
  }
}

// Fetch favorites
async function fetchFavorites(page = 1) {
  favoritesLoading.value = true;

  try {
    const response = await api.get('/me/favorites', {
      params: { page, per_page: favoritesPerPage.value },
    });

    const favoritesData = response.data?.data ?? [];
    const meta = response.data?.meta ?? {};

    favorites.value = favoritesData.map(site => ({
      site_id: site.id,
      name: site.name,
      city: site.city,
    }));

    favoritesPage.value = meta.page ?? page;
    favoritesTotalPages.value = meta.total_pages ?? 1;
  } catch (error) {
    console.error('Error al cargar favoritos:', error);
    favorites.value = [];
    favoritesPage.value = 1;
    favoritesTotalPages.value = 1;
  } finally {
    favoritesLoading.value = false;
  }
}

// Remove favorite
async function removeFavorite(siteId) {
  try {
    await api.delete(`/sites/${siteId}/favorite`);
    favorites.value = favorites.value.filter(fav => fav.site_id !== siteId);
  } catch (error) {
    console.error('Error al eliminar favorito:', error.response?.data || error.message);
  }
}
//Eliminar reseña
async function deleteReview(review) {
  if (!confirm("¿Seguro que querés eliminar esta reseña?")) return;

  try {
    await api.delete(`/sites/${review.site?.id}/reviews/${review.id}`);

    reviews.value = reviews.value.filter(r => r.id !== review.id);

    triggerToast("Reseña eliminada correctamente ");

  } catch (error) {
    console.error("Error al eliminar reseña:", error);
    triggerToast("Error al eliminar reseña ");
  }
}

function triggerToast(message) {
  toastMessage.value = message;
  showToast.value = true;
  setTimeout(() => {
    showToast.value = false;
  }, 5000); 
}



// Event handlers
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

function handleFavoritePageSizeChange(newSize) {
  if (favoritesPerPage.value === newSize) {
    return;
  }

  favoritesPerPage.value = newSize;
  fetchFavorites(1);
}

// Initialize on mount
onMounted(() => {
  fetchReviews(1);
  fetchFavorites(1);
});
</script>
