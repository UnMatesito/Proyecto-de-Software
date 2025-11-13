import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '@/api/axios.js';

export const useSitesStore = defineStore('sites', () => {
  const sites = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  let ongoingRequest = null;

  async function fetchSites(forceRefresh = false) {
    if (!forceRefresh && sites.value.length) {
      return sites.value;
    }

    if (!ongoingRequest) {
      isLoading.value = true;
      error.value = null;

      ongoingRequest = api
        .get('/sites')
        .then(({ data }) => {
          sites.value = data?.data ?? [];
          return sites.value;
        })
        .catch((err) => {
          error.value = err;
          throw err;
        })
        .finally(() => {
          isLoading.value = false;
          ongoingRequest = null;
        });
    }

    return ongoingRequest;
  }

  function getTopSites(limit = 10) {
    return sites.value.slice(0, limit);
  }

  return {
    sites,
    isLoading,
    error,
    fetchSites,
    getTopSites,
  };
});
