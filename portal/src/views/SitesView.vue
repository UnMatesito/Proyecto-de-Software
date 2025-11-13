<template>
    <h2 class="font-semibold text-3xl text-proyecto-primary">Listado de sitios históricos</h2>
    <p class="text-proyecto-accent">Aqui puedes buscar el sitio que justo necesitas.</p>
    <aside class="p-3 ">
      <Filter :page="pagination.page" :tags="tags" :provinces="provinces" @disableMap="changeMapState"></Filter>
      <Map styleContent="height:400px;  width: 100%" :marks="marks" :isDisable="disableMap" @changeMapState="changeMapState"></Map>
    </aside>

    <section class="grid grid-cols-1  md:grid-cols-3 lg:grid-cols-4 gap-3 p-3">
      <Card
      class="  md:max-w-[250px]"
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
      :rating="site.average_rating"
      ></Card>
    </section>

    <Pagination
      :page="pagination.page"
      :pageSize=25
      :totalPages="pagination.total_pages"
      @page-change="pageChanged"
    ></Pagination>
</template>

<script setup>
  import { ref, watch, onMounted} from 'vue'
  import { useRoute, useRouter} from 'vue-router'
  import api from '@/api/axios'
  import Card from '@/components/Card.vue'
  import Pagination from '@/components/Pagination.vue'
  import Filter from '@/components/Filter.vue'
  import Map from '@/components/MapFilter.vue'
  
  const apiMessage = ref('')
  const sites = ref({})
  const pagination = ref({})
  const rout = useRoute()
  const router = useRouter()
  const marks = ref([])
  const tags = ref([])
  const provinces = ref([])
  const disableMap = ref(false)
  const page = ref(1)

  const fetchSites = async (url) => {
    try {
      const { data } = await api.get(rout.fullPath)
      const response = data
      sites.value = response.data
      pagination.value = response.meta
      marks.value = []
      sites.value.forEach(site => {
        marks.value.push({name: site.name, lat: site.lat, lon: site.lon})
      });
    } catch (error) {
      apiMessage.value = '❌ No se pudo conectar con la API'
      console.error(error)
    }
  }
  const fetchTags = async () => {
    const { data } = await api.get("/tags")
    tags.value =  data.data
  }
  const fetchProvinces = async () => {
    const { data } = await api.get("/provinces")
    provinces.value =  data.data
  }

  const changeMapState = (isDisable) => {
    disableMap.value = isDisable
  }

  const pageChanged = (p) => {
    page.value = p
    router.push({
      path: rout.path,
      query: {
        ...rout.query,
        page: p
      }
    })
  }
  onMounted(
     async () => {
      fetchSites()
      fetchTags()
      fetchProvinces()
     }
  )

  watch(rout, () => {
    fetchSites()
  })
</script>
