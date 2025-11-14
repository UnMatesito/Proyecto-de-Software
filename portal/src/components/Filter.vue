<template>
  <form class="m-auto">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
      <select
        id="small"
        v-model="provinceValue"
        @change="fetchCities(provinceValue)"
        class="block max-w-96 p-2 text-sm text-gray-900 border border-gray-300
               rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
               dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
               dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
      >
        <option selected>Provincia</option>
        <option
          v-for="province in provinces"
          :key="province.id"
          :value="province.name"
        >
          {{ province.name }}
        </option>
      </select>

      <div class="relative">
        <div
          class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none"
        >
          <svg
            class="w-4 h-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          type="search"
          v-model="nameValue"
          id="search"
          class="w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg
                 bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700
                 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
                 dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Nombre del sitio"
        />
      </div>

      <div
        v-if="authStore.isAuthenticated"
        class="p-2 border rounded-md text-sm bg-gray-50 focus:ring-blue-500
               focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600
               dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500
               dark:focus:border-blue-500"
      >
        <input
          id="bordered-checkbox-1"
          v-model="favoriteValue"
          type="checkbox"
          class="text-blue-600 bg-gray-100 border-gray-300 rounded-sm
                 focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800
                 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
        />
        <label
          for="bordered-checkbox-1"
          class="w-full ms-2 text-sm font-medium text-gray-900 dark:text-gray-300"
        >
          Favoritos
        </label>
      </div>

      <div
        class="col-start-2 row-start-3 md:col-start-4 md:row-start-1"
        :class="authStore.isAuthenticated ? 'flex flex-col gap-1' : 'flex gap-1'"
      >
        <router-link
          :to="{
            query: {
              ...(nameValue && { name: nameValue }),
              ...(descrpitionValue && { description: descrpitionValue }),
              ...(provinceValue !== 'Provincia' && { province: provinceValue }),
              ...(cityValue !== 'Ciudad' && { city: cityValue }),
              ...(tagsValue.length > 0 && { tags: tagsValue.join() }),
              page: 1,
              favorites: favoriteValue,
              ...(orderByValue !== 'Ordenar por' && { order_by: orderByValue }),
              ...(rout.query.lat && { lat: rout.query.lat }),
              ...(rout.query.lon && { lon: rout.query.lon }),
              ...(rout.query.radius && { radius: rout.query.radius })
            }
          }"
          class="text-white w-full bg-proyecto-primary hover:bg-proyecto-accent
                 focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition
                 font-medium rounded-lg text-sm px-5 py-2.5 text-center
                 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none
                 dark:focus:ring-blue-800"
        >
          Filtrar
        </router-link>
      </div>

      <select
        id="default"
        v-model="cityValue"
        class="block p-2 text-sm text-gray-900 border border-gray-300 rounded-lg
               bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700
               dark:border-gray-600 dark:placeholder-gray-400 dark:text-white
               dark:focus:ring-blue-500 dark:focus:border-blue-500"
      >
        <option selected>Ciudad</option>
        <option
          v-for="city in cities"
          :key="city.id"
          :value="city.name"
        >
          {{ city.name }}
        </option>
      </select>

      <div class="relative">
        <div
          class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none"
        >
          <svg
            class="w-4 h-4 text-gray-500 dark:text-gray-400"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          type="search"
          v-model="descrpitionValue"
          id="search"
          class="block w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300
                 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
                 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
                 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          placeholder="Descripción breve"
        />
      </div>

      <div>
        <select
          id="default"
          v-model="orderByValue"
          class="block w-full p-2 text-sm text-gray-900 border border-gray-300
                 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
                 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
                 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        >
          <option selected>Ordenar por</option>
          <option value="oldest">Últimos creados</option>
          <option value="latest">Primeros creados</option>
          <option value="rating-1-5">Reseñas 1-5 estrellas</option>
          <option value="rating-5-1">Reseñas 5-1 estrellas</option>
        </select>
      </div>

      <router-link
        @click="handleReset"
        :to="{ query: {} }"
        class="text-white w-full bg-proyecto-primary hover:bg-proyecto-accent
               focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition
               font-medium rounded-lg text-sm px-5 py-2.5 text-center
               dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none
               dark:focus:ring-blue-800"
      >
        Restaurar
      </router-link>
    </div>

    <select name="tags" id="tags" multiple>
      <option
        v-for="tag in tags"
        :key="tag.id"
        :value="tag.slug"
      >
        {{ tag.name }}
      </option>
    </select>
    <div></div>
  </form>
</template>

<script setup>
import api from '@/api/axios'
import { ref, watch, nextTick, onMounted, defineEmits } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const emit = defineEmits(['disableMap'])

const cityValue = ref('Ciudad')
const nameValue = ref('')
const descrpitionValue = ref('')
const tagsValue = ref([])
const favoriteValue = ref(false)
const orderByValue = ref('Ordenar por')
const provinceValue = ref('Provincia')

const cities = ref([])

const rout = useRoute()
const props = defineProps(['provinces', 'states', 'page', 'tags'])

function loadFromRoute(q = rout.query) {
  nameValue.value = q.name ?? ''
  descrpitionValue.value = q.description ?? ''
  provinceValue.value = q.province ?? 'Provincia'
  cityValue.value = q.city ?? 'Ciudad'
  orderByValue.value = q.order_by ?? 'Ordenar por'
  favoriteValue.value = q.favorites === 'true' || q.favorites === true

  if (q.tags) {
    const raw = Array.isArray(q.tags) ? q.tags.join(',') : q.tags
    tagsValue.value = raw.split(',').map(t => t.trim()).filter(Boolean)
  } else {
    tagsValue.value = []
  }
}

function destroyMultiSelect() {
  const prev = document.querySelector('.multi-select-tag')
  if (prev) prev.remove()
}

function initMultiSelect() {
  // Sincronizar atributos selected del <select> con tagsValue ANTES de crear MultiSelectTag
  const tagsSelect = document.getElementById('tags')
  if (tagsSelect) {
    Array.from(tagsSelect.options).forEach(opt => {
      opt.selected = tagsValue.value.includes(opt.value)
    })
  }

  destroyMultiSelect()

  new MultiSelectTag('tags', {
    rounded: true,
    shadow: true,
    placeholder: 'Seleccionar tags',
    onChange(selected) {
      tagsValue.value = selected.map(e => e.id)
      console.log('Tags seleccionados:', tagsValue.value)
    }
  })

  const inputTag = document.getElementById('tag-input')
  const container = document.getElementsByClassName('multi-select-tag')

  if (inputTag && container[0]) {
    container[0].classList.add('col-start-1-i', 'col-end-4-i')
    inputTag.className = 'w-full'
    inputTag.setAttribute('readonly', '')
  }

  const dropdown = document.getElementById('dropdown')
  if (dropdown) dropdown.style.zIndex = '1200'
}

const fetchCities = async (provinceName) => {
  const province = props.provinces.find(p => p.name === provinceName)
  if (province) {
    const idProvince = province.id
    const { data } = await api.get(`provinces/${idProvince}/cities`)
    // Solo resetear cityValue si NO viene de la URL
    if (!rout.query.city) {
      cityValue.value = 'Ciudad'
    }
    cities.value = data.data
  } else {
    cities.value = []
  }
}

const disableMapClick = () => emit('disableMap', true)

const handleReset = () => {
  nameValue.value = ''
  descrpitionValue.value = ''
  provinceValue.value = 'Provincia'
  cityValue.value = 'Ciudad'
  orderByValue.value = 'Ordenar por'
  favoriteValue.value = false
  tagsValue.value = []
  cities.value = []

  disableMapClick()

  nextTick(() => {
    initMultiSelect()
  })
}

// Inicialización principal
loadFromRoute()

onMounted(async () => {
  // Si la URL trae provincia, cargar ciudades
  if (provinceValue.value !== 'Provincia') {
    await fetchCities(provinceValue.value)
  }
  // Inicializar multiselect después de montar
  await nextTick()
  initMultiSelect()
})

// Cuando cambian los tags reconstruir el multiselect
watch(
  () => props.tags,
  async (newTags) => {
    if (newTags && newTags.length > 0) {
      await nextTick()
      initMultiSelect()
    }
  }
)

// Mantener formulario sincronizado si cambia la URL (ej: botón atrás del navegador)
watch(
  () => rout.query,
  async (newQuery) => {
    loadFromRoute(newQuery)
    if (provinceValue.value !== 'Provincia') {
      await fetchCities(provinceValue.value)
    } else {
      cities.value = []
    }
    await nextTick()
    initMultiSelect()
  }
)
</script>

<style>
.col-start-1-i {
  grid-column-start: 1 !important;
}
.col-end-4-i {
  grid-column-end: 4 !important;
}
</style>
