<template>
    <div class="bg-proyecto-accent w-screen h-[35rem] text-white flex items-center justify-evenly mb-8 shadow-xl">
      <img src="../assets/images/mapa.png" alt="gif mapa" class="h-[40rem] pointer-events-none select-none"/>
      <div>
        <h1 class="text-8xl font-bold">Histori.ar</h1>
        <p class="font-medium text-xl">Donde cada lugar tiene una historia que contar.</p>
        <form class="max-w-md mx-auto mt-8">
            <label for="default-search" class="mb-2 text-sm font-medium text-gray-900 sr-only">Search</label>
            <div class="relative">
                <div class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                    <i class="fa-solid fa-magnifying-glass text-black mx-1"></i>
                </div>
                <input type="search" id="default-search" class="block w-full p-4 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-proyecto-primary focus:border-proyecto-primary" placeholder="¿Que estas Buscando?" required />
                <ButtonPrimary type="submit" text="Buscar" class="absolute end-2.5 bottom-2"/>
            </div>
        </form>
      </div>
    </div>

    <div class="w-3/4 mb-8 mx-auto">
      <!-- Sección de Más Visitados -->
      <Section title="Más Visitados"/>

      <!-- Seccion Mejor Puntuados -->
      <Section title="Mejor Puntuados"/>

      <!-- Seccion Favoritos del usuario-->
      <Section title="Tus Favoritos"/>

      <!-- Seccion recientemente agregados-->
      <Section title="Recientemente Agregados"/>
    </div>

    <button
      @click="fetchExample"
      class="bg-proyecto-primary text-white font-semibold px-4 py-2 rounded-lg hover:bg-proyecto-accent transition"
    >
      Probar conexión con API Flask
    </button>

    <p v-if="apiMessage" class="mt-4 text-proyecto-accent font-medium">
      {{ apiMessage }}
    </p>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/axios'
import Card from "@/components/Card.vue";
import Section from "@/components/Section.vue";
import ButtonPrimary from "@/components/buttons/ButtonPrimary.vue";

const apiMessage = ref('')

const fetchExample = async () => {
  try {
    const { data } = await api.get('/ping')
    apiMessage.value = data.message || JSON.stringify(data)
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API'
    console.error(error)
  }
}
</script>
