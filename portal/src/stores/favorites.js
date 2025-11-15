import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import api from '@/api/axios.js';
import { useAuthStore } from '@/stores/auth.js';

export const useFavoritesStore = defineStore('favorites', () => {
  const authStore = useAuthStore();
  const favorites = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  let ongoingRequest = null;

  const CACHE_TTL = 30 * 1000;
  const lastFetchedAt = ref(null);

  function cacheIsValid() {
    if (!lastFetchedAt.value) return false;
    return (Date.now() - lastFetchedAt.value) < CACHE_TTL;
  }

  async function fetchFavorites(forceRefresh = false) {
    if (!authStore.isAuthenticated) {
      resetFavorites();
      return favorites.value;
    }

    if (!forceRefresh && favorites.value.length && cacheIsValid()) {
      return favorites.value;
    }

    if (ongoingRequest) {
      return ongoingRequest;
    }

    isLoading.value = true;
    error.value = null;

    ongoingRequest = api
      .get('/me/favorites')
      .then(({ data }) => {
        favorites.value = (data?.data ?? []).map(site => site.id);
        lastFetchedAt.value = Date.now();   // renovar TTL
        return favorites.value;
      })
      .catch(err => {
        favorites.value = [];
        error.value = err;
        throw err;
      })
      .finally(() => {
        isLoading.value = false;
        ongoingRequest = null;
      });

    return ongoingRequest;
  }

  function resetFavorites() {
    favorites.value = [];
    error.value = null;
    ongoingRequest = null;
    lastFetchedAt.value = null;
  }

  function isFavorite(siteId) {
    return favorites.value.includes(siteId);
  }

  function addFavoriteLocally(siteId) {
    if (!isFavorite(siteId)) {
      favorites.value = [...favorites.value, siteId];
    }
  }

  function removeFavoriteLocally(siteId) {
    favorites.value = favorites.value.filter((favoriteId) => favoriteId !== siteId);
  }

  async function addFavorite(siteId) {
    await api.put(`/sites/${siteId}/favorite`);
    addFavoriteLocally(siteId);
    lastFetchedAt.value = Date.now();
  }

  async function removeFavorite(siteId) {
    await api.delete(`/sites/${siteId}/favorite`);
    removeFavoriteLocally(siteId);
    lastFetchedAt.value = Date.now();
  }

  async function toggleFavorite(siteId) {
    if (!authStore.isAuthenticated) {
      return;
    }

    if (isFavorite(siteId)) {
      await removeFavorite(siteId);
    } else {
      await addFavorite(siteId);
    }
  }

  watch(
    () => authStore.isAuthenticated,
    (isAuthenticated) => {
      if (!isAuthenticated) {
        resetFavorites();
      }
    }
  );

  return {
    favorites,
    isLoading,
    error,
    fetchFavorites,
    resetFavorites,
    isFavorite,
    toggleFavorite,
    addFavoriteLocally,
    removeFavoriteLocally,
    lastFetchedAt
  };
});
