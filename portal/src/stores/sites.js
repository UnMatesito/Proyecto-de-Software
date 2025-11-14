import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api/axios.js';

export const useSitesStore = defineStore('sites', () => {
  const sites = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  let ongoingRequest = null;

  const CACHE_TTL = 60 * 1000; // 60 segundos
  const lastFetchedAt = ref(null);

  function cacheIsValid() {
    if (!lastFetchedAt.value) return false;
    return (Date.now() - lastFetchedAt.value) < CACHE_TTL;
  }

  async function fetchSites(forceRefresh = false) {
    if (!forceRefresh && sites.value.length && cacheIsValid()) {
      return sites.value;
    }

    if (ongoingRequest) {
          return ongoingRequest;
    }

    isLoading.value = true;
    error.value = null;

    ongoingRequest = (async () => {
      try {
        let allSites = [];
        let currentPage = 1;
        let totalPages = 1;

        do {
          const { data } = await api.get('/sites', {
            params: {
              page: currentPage,
              per_page: 20
            }
          });

          const newSites = data?.data ?? [];
          allSites = [...allSites, ...newSites];

          totalPages = data?.meta?.total_pages ?? 1;
          currentPage++;
        } while (currentPage <= totalPages);

        sites.value = allSites;
        lastFetchedAt.value = Date.now();   // ⏱️ renovar el TTL

        return sites.value;

      } catch (err) {
        error.value = err;
        throw err;

      } finally {
        isLoading.value = false;
        ongoingRequest = null;
      }
    })();

    return ongoingRequest;
  }

  function getRecentlyAddedSites(limit = 10) {
    return [...sites.value]
      .sort((a, b) => new Date(b.inserted_at) - new Date(a.inserted_at))
      .slice(0, limit);
  }

  function getTopScoredSites(limit = 10) {
    return [...sites.value]
      .sort((a, b) => {
        const ratingA = a.average_rating ?? 0;
        const ratingB = b.average_rating ?? 0;
        return ratingB - ratingA;
      })
      .slice(0, limit);
  }

  function getUserFavoriteSites(userFavorites) {
    return sites.value.filter(site => userFavorites.includes(site.id));
  }

  return {
    sites,
    isLoading,
    error,
    fetchSites,
    getRecentlyAddedSites,
    getTopScoredSites,
    getUserFavoriteSites,
    lastFetchedAt
  };
});
