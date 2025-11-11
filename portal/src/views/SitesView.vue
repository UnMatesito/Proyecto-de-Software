<template>
    <h2 class="font-semibold text-3xl">Listado de sitios históricos</h2>
    <p>Aqui puedes buscar el sitio que justo necesitas.</p>
    <aside class="p-3">
      <Filter :page="pagination.page"></Filter>
      <Map styleContent="height:400px;  width: 100%" :marks="marks"></Map>

    </aside>

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
      :id="site.id"
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
  import Filter from '@/components/Filter.vue'
  import Map from '@/components/Map.vue'
  const apiMessage = ref('')
  const sites = ref({})
  const pagination = ref({})
  const rout = useRoute()
  const marks = ref([])
  const fetchSites = async (url) => {
    try {
      const { data } = await api.get(rout.fullPath)
      const response = data
      sites.value = response.data
      pagination.value = response.meta
      console.log(sites.value)
      sites.value.forEach(site => {
        marks.value.push({name: site.name, lat: site.lat, long: site.long})
      });
    } catch (error) {
      apiMessage.value = '❌ No se pudo conectar con la API'
      console.error(error)
    }
  }
  onMounted(
      () => fetchSites()
  )
  watch(rout, () => {
    fetchSites()
    console.log("fetch")
  })
</script>
