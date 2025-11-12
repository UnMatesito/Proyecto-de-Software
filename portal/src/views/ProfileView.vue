<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <h1 class="text-3xl font-bold mb-6 text-gray-800">Mi Perfil</h1>

    <div v-if="user" class="bg-white p-6 rounded-lg shadow-md mb-8 flex items-center space-x-4">
      <img
        :src="user.avatar || 'https://via.placeholder.com/150'"
        alt="Avatar"
        class="w-20 h-20 rounded-full border-2 border-gray-300 object-cover"
        referrerpolicy="no-referrer"
      >
      <div>
        <h2 class="text-2xl font-semibold text-gray-700">{{ user.name }}</h2>
        <p class="text-gray-500">{{ user.email }}</p>
      </div>
    </div>
    <div v-else class="bg-white p-6 rounded-lg shadow-md mb-8 text-center text-gray-500">
      Cargando información del usuario...
    </div>

    <div class="mb-4 border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          @click="activeTab = 'reviews'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'reviews'
              ? 'border-proyecto-primary text-proyecto-primary'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Mis Reseñas
        </button>
        <button
          @click="activeTab = 'favorites'"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm',
            activeTab === 'favorites'
              ? 'border-proyecto-primary text-proyecto-primary'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          ]"
        >
          Mis Sitios Favoritos
        </button>
      </nav>
    </div>

    <div>
      <div v-if="loading" class="text-center py-10">
        <p class="text-gray-500">Cargando...</p>
      </div>

      <div v-else>
        <div v-show="activeTab === 'reviews'">
          <h3 class="text-xl font-semibold mb-4 text-gray-700">Mis Reseñas</h3>

          <div v-if="reviewsLoading" class="text-center py-5">Cargando reseñas...</div>

          <div v-else>
            <ul v-if="reviews.length > 0" class="space-y-4">
              <li v-for="review in reviews" :key="review.site_id" class="bg-white p-4 rounded-lg shadow">
                <p><strong>Sitio:</strong> {{ review.name }}</p>
                <div class="flex items-center">
                  <strong class="mr-2">Calificación:</strong>
                  <RatingStars :rating="review.rating" />
                </div>
                <p><strong>Fecha:</strong> {{ new Date(review.created_at).toLocaleDateString() }}</p>
                <p class="mt-2 text-gray-600">{{ review.comment_excerpt }}</p>
              </li>
            </ul>
            <p v-else class="text-gray-500 italic">Aún no escribiste reseñas.</p>

          <div class="flex justify-center mt-6">
            <Pagination
              :page="reviewsPage"
              :pages="reviewsTotalPages"
              @page-changed="handleReviewPageChange"
              class="mt-6"
            />
          </div>
          </div>
        </div>

        <div v-show="activeTab === 'favorites'">
            <h3 class="text-xl font-semibold mb-4 text-gray-700">Mis Sitios Favoritos</h3>

            <div v-if="favoritesLoading" class="text-center py-5">Cargando favoritos...</div>

            <div v-else>
              <ul v-if="favorites.length > 0" class="space-y-4">
                <li v-for="fav in favorites" :key="fav.site_id" class="bg-white p-4 rounded-lg shadow flex justify-between items-center">
                  <div>
                    <p class="font-medium">{{ fav.name }}</p>
                    <p class="text-sm text-gray-500">{{ fav.city }}</p>
                  </div>
                  <div class="flex flex-row items-center space-x-4">
                    <a :href="`/sites/${fav.site_id}`" class="text-proyecto-primary hover:underline text-sm">Ver sitio</a>
                    <button @click="removeFavorite(fav.site_id)" class="rounded-lg bg-red-500 text-white px-1.5 py-1 focus:ring-2 focus:ring-red-300 text-sm" >Quitar de Favoritos</button>
                  </div>
                </li>
              </ul>
              <p v-else class="text-gray-500 italic">Aún no marcaste ningún sitio como favorito.</p>

            <div class="flex justify-center mt-6">
              <Pagination
                :page="favoritesPage"
                :pages="favoritesTotalPages"
                @page-changed="handleFavoritePageChange"
                class="mt-6"
              />
            </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import RatingStars from '@/components/Stars.vue';
import { useAuthStore } from '@/stores/auth';
import api from '../api/axios.js';
import Pagination from '@/components/Pagination.vue';

const authStore = useAuthStore();
const user = authStore.user;

const activeTab = ref('reviews');
const loading = ref(true);

const reviews = ref([]);
const reviewsPage = ref(1);
const reviewsTotalPages = ref(1);
const reviewsLoading = ref(true);

const favorites = ref([]);
const favoritesPage = ref(1);
const favoritesTotalPages = ref(1);
const favoritesLoading = ref(true);


const mockReviews = {
  items: [
    { site_id: 1, name: 'Museo de Arte Moderno', rating: 5, created_at: '2025-10-28T10:30:00Z', comment_excerpt: '¡Increíble!...' },
    { site_id: 2, name: 'Plaza Central Histórica', rating: 4, created_at: '2025-09-15T14:00:00Z', comment_excerpt: 'Un lugar muy lindo...' }
  ],
  pagination: { page: 1, pages: 3, total: 30, per_page: 25 }
};

const mockFavorites = {
  items: [
    { site_id: 3, name: 'Antigua Biblioteca Nacional', city: 'Ciudad Capital' },
    { site_id: 4, name: 'Faro del Fin del Mundo', city: 'Patagonia' }
  ],
  pagination: { page: 1, pages: 2, total: 20, per_page: 25 }
};

async function fetchListData(listType, page = 1) {
  const isLoadingRef = listType === 'reviews' ? reviewsLoading : favoritesLoading;
  const itemsRef = listType === 'reviews' ? reviews : favorites;
  const pageRef = listType === 'reviews' ? reviewsPage : favoritesPage;
  const totalPagesRef = listType === 'reviews' ? reviewsTotalPages : favoritesTotalPages;

  isLoadingRef.value = true;

  try {
    const endpoint = listType === 'reviews' ? '/me/reviews' : '/me/favorites';
    const response = await api.get(endpoint, { params: { page } });

    // API real usa data + meta
    if (endpoint === '/me/favorites') {
      const favoritesData = response.data.data || [];
      const meta = response.data.meta || {};

      itemsRef.value = favoritesData.map(site => ({
        site_id: site.id,
        name: site.name,
        city: site.city,
      }));

      pageRef.value = meta.page || 1;
      // Calcular cantidad de páginas
      totalPagesRef.value = Math.ceil((meta.total || 1) / (meta.per_page || 1));
    }
  } catch (error) {
    console.warn(`⚠️ No se pudo conectar con ${listType}. Usando datos mock.`);
    const mockData = listType === 'reviews' ? mockReviews : mockFavorites;
    itemsRef.value = mockData.items;
    pageRef.value = mockData.pagination.page;
    totalPagesRef.value = mockData.pagination.pages;
  } finally {
    isLoadingRef.value = false;
    if (!reviewsLoading.value && !favoritesLoading.value) {
      loading.value = false;
    }
  }
}

onMounted(() => {
  fetchListData('reviews', 1);
  fetchListData('favorites', 1);
});

function handleReviewPageChange(newPage) {
  fetchListData('reviews', newPage);
}

function handleFavoritePageChange(newPage) {
  fetchListData('favorites', newPage);
}

function removeFavorite(siteId) {
  api.delete(`/sites/${siteId}/favorite`)
  .then(() => {
    favorites.value = favorites.value.filter(fav => fav.site_id !== siteId)
    console.log(`✅ Sitio ${siteId} eliminado de favoritos.`)
  })
  .catch(error => {
    console.error('❌ Error al eliminar favorito:', error.response?.data || error.message)
  })
}
</script>
