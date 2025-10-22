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
    <Pagination 
    :page="pagination.page"
    :per_page="pagination.per_page"
    :total="pagination.total"
    pages=6
    ></Pagination>
</template>

<script setup>
import { ref, watch, onMounted} from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/axios'
import Card from '@/components/Card.vue'
import Pagination from '@/components/Pagination.vue'
const apiMessage = ref('')
const sites = ref({})
const pagination = ref({})
const root = useRoute()

const fetchSites = async (url) => {
  try {
    const { data } = await api.get(url)
    const response = data
    sites.value = response.data
    pagination.value = response.meta
  } catch (error) {
    apiMessage.value = '❌ No se pudo conectar con la API'
    console.error(error)
  }
}
onMounted(
    () => fetchSites()
)
watch(root, 
  () => {
  fetchSites(query)
})
</script>