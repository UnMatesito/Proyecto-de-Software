<template>
  <main class="min-h-screen flex flex-col items-center justify-center p-6">
    <h1 class="text-4xl font-bold text-proyecto-primary mb-4">
      Portal Público
    </h1>
    <p class="text-lg text-gray-700 mb-6 text-center">
      Bienvenido al portal público del Proyecto de Software.
    </p>

    <button
      @click="fetchExample"
      class="bg-proyecto-primary text-white font-semibold px-4 py-2 rounded-lg hover:bg-proyecto-accent transition"
    >
      Probar conexión con API Flask
    </button>

    <p v-if="apiMessage" class="mt-4 text-proyecto-accent font-medium">
      {{ apiMessage }}
    </p>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const apiMessage = ref('')

const fetchExample = async () => {
  try {
    const { data } = await axios.get(
      `${import.meta.env.VITE_API_URL}/ping`
    )
    apiMessage.value = data.message || JSON.stringify(data)
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API'
    console.error(error)
  }
}
</script>
