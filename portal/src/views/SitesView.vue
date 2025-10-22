<template>
    <h2>Listado de sitios históricos</h2>
    <section class="grid md:grid-cols-4 gap-3 p-3">  
      <Card
      v-for="site in sites"
      :key="`${site.id}-${site.name}`"
      :name="site.name"
      :province="site.province"
      :city="site.city"
      :tags="site.tags"
      :state_of_conservation="site.state_of_conservation"
      :inauguration_year="site.inauguration_year"
      :category="site.category"
      :imagen="site.imagen"
      ></Card>
    </section>
</template>

<script setup>
import { ref, watchEffect} from 'vue'
import api from '@/api/axios'
import Card from '@/components/Card.vue'

const apiMessage = ref('')
const sites = ref()

const fetchSites = async () => {
  try {
    const { data } = await api.get('/sites')
    const response = data
    sites.value = response.data
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API'
    console.error(error)
  }
}
watchEffect(
    () => fetchSites()
)
</script>