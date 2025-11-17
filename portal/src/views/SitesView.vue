<template>
  <div class="flex flex-col items-center p-3 w-full">
    <h2 class="font-semibold text-3xl text-proyecto-primary">Listado de sitios históricos</h2>
    <p class="text-proyecto-accent">Aqui puedes buscar el sitio que justo necesitas.</p>
    <aside class="p-3 max-w-[1150px]">
      <Filter :page="pagination.page" :tags="tags" :provinces="provinces" @disableMap="changeMapState" />
      <Map styleContent="height:400px;  width: 100%" :marks="marks" :isDisable="disableMap" @changeMapState="changeMapState" />
    </aside>

    <section class="w-full sm:w-auto grid  sm:grid-cols-2  md:grid-cols-3  lg:grid-cols-3 xl:grid-cols-4 gap-3 p-3">
      <Card
      class="md:w-[230px] lg:w-[270px]"
      v-for="site in sites"
      :key="`${site.id}-${site.name}`"
      :name="site.name"
      :province="site.province"
      :city="site.city"
      :tags="site.tags"
      :average_rating="site.average_rating"
      :state_of_conservation="site.state_of_conservation"
      :inauguration_year="site.inauguration_year"
      :category="site.category"
      :imagen="site.images[0].url"
      :alt-imagen="site.images[0].alt"
      :id="site.id"
      :rating="site.average_rating"
      :created_at="site.inserted_at"
      />
      <SkeletonCard v-if="!sites" v-for="n in 24" />
    </section>

    <Pagination
      class="md:justify-center mb-3"
      :page="pagination.page"
      :pageSize=25
      :totalPages="pagination.total_pages"
      @page-change="pageChanged" />
  </div>
</template>

<script setup>
  import { ref, watch, onMounted} from 'vue'
  import { useRoute, useRouter} from 'vue-router'
  import {useAuthStore} from "@/stores/auth.js";
  import api from '@/api/axios'
  import Card from '@/components/Card.vue'
  import Pagination from '@/components/Pagination.vue'
  import Filter from '@/components/Filter.vue'
  import Map from '@/components/MapFilter.vue'
  import SkeletonCard from '@/components/SkeletonCard.vue'
  const authStore = useAuthStore()
  const apiMessage = ref('')
  const sites = ref(null)
  const pagination = ref({})
  const rout = useRoute()
  const router = useRouter()
  const marks = ref([])
  const tags = ref([])
  const provinces = ref([])
  const disableMap = ref(false)
  const page = ref(1)

  //Fetch para obtener los sitios
  const fetchSites = async (url) => {
    try {

      if (rout.query.favorites && !authStore.isAuthenticated) {
        sites.value = []       // No mostrar skeleton
        pagination.value = { total_pages: 0, page: 1 }
        marks.value = []
        return
      }

      sites.value = null // Para activar skeleton

      const { data } = await api.get(rout.fullPath)

      const response = data
      sites.value = response.data
      pagination.value = response.meta
      marks.value = []
      sites.value.forEach(site => {
        marks.value.push({name: site.name, lat: site.lat, lon: site.lon, desc: site.short_description})
      });
    } catch (error) {
      apiMessage.value = '❌ No se pudo conectar con la API'
      console.error(error)
      sites.value = []
      marks.value = []
    }
  }

  //Obtener los tags para el filtrado de los sitios
  const fetchTags = async () => {
    const { data } = await api.get("/tags")
    tags.value =  data.data
  }

  //Obtener las provicias filtrado de los sitios
  const fetchProvinces = async () => {
    const { data } = await api.get("/provinces")
    provinces.value =  data.data
  }

  //Captura el emit enviado por el filter que desactiva el radio de búsqueda
  const changeMapState = (isDisable) => {
    disableMap.value = isDisable
  }

  //Cambia de pagina y actualiza la URL
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

  //Hace los fetch una vez que el componente se cargue
  onMounted(
     async () => {
      fetchSites()
      fetchTags()
      fetchProvinces()
     }
  )

  //Actualiza los sitios cada vez que la URL cambia
  watch(rout, () => {
    fetchSites()
  })

</script>
