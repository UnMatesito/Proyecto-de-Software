<template>
  <div class="flex flex-col items-center justify-center py-12">
    <h2 class="text-3xl font-bold text-proyecto-primary mb-4">
      Bienvenido
    </h2>
    <p class="text-lg text-gray-700 mb-6 text-center">
      Portal público del Proyecto de Software
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api/axios'

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
