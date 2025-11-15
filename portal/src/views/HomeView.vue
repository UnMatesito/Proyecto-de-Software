<template>
    <div class="bg-proyecto-accent w-full h-[22rem] sm:h-[35rem] text-white flex items-center justify-evenly mb-8 shadow-xl">
      <img src="../assets/images/mapa.png" alt="gif mapa" class="hidden sm:block sm:h-[22rem] lg:h-[40rem] pointer-events-none select-none transition-transform"/>
      <div>
        <h1 class="text-7xl md:text-8xl font-bold text-center">Histori.ar</h1>
        <p class="font-medium sm:text-xl text-center">Donde cada lugar tiene una historia que contar.</p>
        <form class="max-w-md mx-auto mt-8" @submit.prevent="onSearch">
            <label for="default-search" class="mb-2 text-sm font-medium text-gray-900 sr-only">Buscar</label>
            <div class="relative">
                <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                    <i class="fa-solid fa-magnifying-glass text-black mx-1"></i>
                </div>
                <input type="search" id="default-search" v-model="searchQuery" class="block w-full p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-proyecto-primary focus:border-proyecto-primary" placeholder="¿Cuál es tu próxima aventura?" required />
                <ButtonPrimary type="submit" text="Buscar" class="absolute end-2.5 bottom-1.5"/>
            </div>
        </form>
      </div>
    </div>

    <div class="mx-4 w-[90%]">
      <!-- Seccion Mejor Puntuados -->
      <TopRatedSection />

      <!-- Seccion Favoritos del usuario-->
      <FavoritesSection />

      <!-- Seccion recientemente agregados-->
      <RecentlySection />
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/axios'
import ButtonPrimary from "@/components/buttons/ButtonPrimary.vue";
import RecentlySection from "@/components/RecentlySection.vue";
import FavoritesSection from "@/components/FavoritesSection.vue";
import TopRatedSection from "@/components/TopRatedSection.vue";

const apiMessage = ref('')
const searchQuery = ref('')
const router = useRouter()

const fetchExample = async () => {
  try {
    const { data } = await api.get('/ping')
    apiMessage.value = data.message || JSON.stringify(data)
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API'
    console.error(error)
  }
}

const onSearch = () => {
  if (!searchQuery.value.trim()) return

  router.push({
    path: '/sites',
    query: { name: searchQuery.value.trim() }
  })
}
</script>
