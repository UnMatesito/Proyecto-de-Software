<script setup>
    import { computed, onMounted, ref, watch } from "vue";
    import { storeToRefs } from "pinia";
    import { useAuthStore } from '@/stores/auth.js';
    import { useSitesStore } from '@/stores/sites.js';
    import { useFavoritesStore } from '@/stores/favorites.js';
    import CardList from "@/components/CardList.vue";

    const authStore = useAuthStore();
    const sitesStore = useSitesStore();
    const favoritesStore = useFavoritesStore();
    const { isAuthenticated } = storeToRefs(authStore);

    const apiMessage = ref('');

    const sites = computed(() => {
        // Manejar tanto si favorites son objetos como si son IDs directamente
        const userFavorites = favoritesStore.favorites.map(fav =>
            typeof fav === 'object' ? fav.site_id : fav
        );
        return sitesStore.getUserFavoriteSites(userFavorites);
    });

    const isFavorite = (siteId) => {
        return favoritesStore.isFavorite(siteId);
    };

    const toggleFavorite = async (siteId) => {
        try {
            await favoritesStore.toggleFavorite(siteId);
        } catch (error) {
            console.error('Error al modificar favoritos:', error);
        }
    };

    const fetchSites = async () => {
        try {
            await sitesStore.fetchSites();
        } catch (error) {
            apiMessage.value = '❌ No se pudo conectar con la API';
            console.error(error);
        }
    };

    const fetchFavorites = async () => {
        try {
            await favoritesStore.fetchFavorites();
        } catch (error) {
            console.error('Error al obtener favoritos:', error);
        }
    };

    onMounted(async () => {
        await fetchSites();
        await fetchFavorites();
    });

    watch(
        () => isAuthenticated.value,
        async (loggedIn) => {
            if (loggedIn) {
                await fetchFavorites();
            }
        }
    );
</script>

<template>
    <div class="mb-8">
        <div class="flex flex-row justify-between items-center mb-4">
            <h2 class="text-2xl sm:text-4xl text-proyecto-primary font-semibold">Tus Favoritos</h2>
            <router-link
              to="/sites?favorites=true"
              class="text-sm sm:text-md font-semibold hover:bg-proyecto-primary hover:text-white rounded-full px-2.5 sm:px-4 py-1 sm:py-2 transition-colors duration-400"
            >
              Ver Todos <i class="fa-solid fa-chevron-right ml-1"></i>
            </router-link>
        </div>
        <div v-if="apiMessage" class="mb-4 rounded-md bg-red-100 px-4 py-2 text-sm text-red-700">
        {{ apiMessage }}
        </div>
        <CardList v-if="isAuthenticated"
            :sites="sites"
            :is-authenticated="isAuthenticated"
            :is-favorite="isFavorite"
            :toggle-favorite="toggleFavorite"
            :hide-favorite-button="true"
        />
        <div v-else class="h-[200px] flex justify-center items-center">
            <p class="px-5 py-2 text-white bg-proyecto-primary/80 text-center rounded-full inline-flex font-semibold shadow-md select-none"> Inicia sesión para ver tus favoritos!</p>
        </div>
    </div>
</template>
