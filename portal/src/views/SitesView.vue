<template>
    <h2>Listado de sitios históricos</h2>
    <section>
        {{ apiMessage }}
    </section>
</template>

<script setup>
import { ref, watchEffect} from 'vue'
import api from '@/api/axios'
import Card from '@/components/Card.vue'

const apiMessage = ref('')

const fetchSites = async () => {
  try {
    const { data } = await api.get('/sites')
    apiMessage.value = data.message || JSON.stringify(data)
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API'
    console.error(error)
  }
}
watchEffect(
    () => fetchSites()
)
</script>