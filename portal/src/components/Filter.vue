<template>
  <form class="m-auto">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
      <!-- Provincia -->
      <select
        id="small"
        v-model="provinceValue"
        @click="fetchCities(provinceValue)"
        class="block max-w-96 p-2 text-sm text-gray-900 border border-gray-300
               rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
               dark:bg-gray-700 dark:border-gray-600 dark:text-white"
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

      <!-- Nombre -->
      <div class="relative">
        <div
          class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none"
        >
          <svg
            class="w-4 h-4 text-gray-500 dark:text-gray-400"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          type="search"
          v-model="nameValue"
          class="w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300 rounded-lg
                 bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700
                 dark:border-gray-600 dark:text-white"
          placeholder="Nombre del sitio"
        />
      </div>

      <!-- Favoritos -->
      <div
        v-if="authStore.isAuthenticated"
        class="p-2 border rounded-md text-sm bg-gray-50 dark:bg-gray-700
               dark:border-gray-600 dark:text-white"
      >
        <input
          id="bordered-checkbox-1"
          v-model="favoriteValue"
          type="checkbox"
          class="text-blue-600 bg-gray-100 border-gray-300 rounded-sm"
        />
        <label for="bordered-checkbox-1" class="ms-2 text-sm font-medium">
          Favoritos
        </label>
      </div>

      <!-- Botón filtrar -->
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
              lat: rout.query.lat,
              lon: rout.query.lon,
              radius: rout.query.radius
            }
          }"
          class="text-white w-24 bg-proyecto-primary hover:bg-proyecto-accent
                 focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition
                 font-medium rounded-lg text-sm px-5 py-2.5 text-center"
        >
          Filtrar
        </router-link>
      </div>

      <!-- Ciudad -->
      <select
        id="default"
        v-model="cityValue"
        class="block p-2 text-sm text-gray-900 border border-gray-300 rounded-lg
               bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700
               dark:border-gray-600 dark:text-white"
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

      <!-- Descripción -->
      <div class="relative">
        <div
          class="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none"
        >
          <svg
            class="w-4 h-4 text-gray-500 dark:text-gray-400"
            fill="none"
            viewBox="0 0 20 20"
          >
            <path
              stroke="currentColor"
              stroke-width="2"
              d="m19 19-4-4m0-7A7 7 0 1 1 1 8a7 7 0 0 1 14 0Z"
            />
          </svg>
        </div>
        <input
          type="search"
          v-model="descrpitionValue"
          class="w-full p-2 ps-10 text-sm text-gray-900 border border-gray-300
                 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
                 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
          placeholder="Descripción breve"
        />
      </div>

      <!-- Ordenar -->
      <div>
        <select
          v-model="orderByValue"
          class="block w-full p-2 text-sm text-gray-900 border border-gray-300
                 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
                 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
        >
          <option selected>Ordenar por</option>
          <option value="oldest">Últimos creados</option>
          <option value="latest">Primeros creados</option>
          <option value="rating-1-5">Reseñas 1-5 estrellas</option>
          <option value="rating-5-1">Reseñas 5-1 estrellas</option>
        </select>
      </div>

      <!-- Restaurar -->
      <router-link
        @click="handleReset"
        :to="{ query: {} }"
        class="text-white w-24 bg-proyecto-primary hover:bg-proyecto-accent
               focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition
               font-medium rounded-lg text-sm px-5 py-2.5"
      >
        Restaurar
      </router-link>

      <!-- Tags multiselect dentro del grid -->
      <div class="col-span-2 md:col-span-4">
        <select name="tags" id="tags" multiple>
          <option
            v-for="tag in tags"
            :key="tag.id"
            :value="tag.slug"
          >
            {{ tag.name }}
          </option>
        </select>
      </div>
    </div>
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

// --- Cargar valores desde la URL ---
function loadFromRoute(q = rout.query) {
  nameValue.value = q.name ?? ''
  descrpitionValue.value = q.description ?? ''
  provinceValue.value = q.province ?? 'Provincia'
  cityValue.value = q.city ?? 'Ciudad'
  orderByValue.value = q.order_by ?? 'Ordenar por'
  favoriteValue.value = q.favorites === 'true' || q.favorites === true

  if (q.tags) {
    // Puede venir como string "a,b,c" o array
    const raw = Array.isArray(q.tags) ? q.tags.join(',') : q.tags
    tagsValue.value = raw.split(',').map(t => t.trim()).filter(Boolean)
  } else {
    tagsValue.value = []
  }
}

// --- Multiselect ---
function destroyMultiSelect() {
  const prev = document.querySelectorAll('.multi-select-tag')
  if (prev && prev.length) {
    prev.forEach(el => el.remove())
  }
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

  // eslint-disable-next-line no-undef
  new MultiSelectTag('tags', {
    rounded: true,
    shadow: true,
    placeholder: 'Seleccionar tags',
    onChange(selected) {
      tagsValue.value = selected.map(e => e.id)
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

// --- Cargar ciudades de una provincia ---
const fetchCities = async (provinceName) => {
  const province = props.provinces.find(p => p.name === provinceName)
  if (province) {
    const { data } = await api.get(`provinces/${province.id}/cities`)
    cityValue.value = 'Ciudad'
    cities.value = data.data
  } else {
    cities.value = []
  }
}

// --- Deshabilitar mapa ---
const disableMapClick = () => emit('disableMap', true)

// --- Reset completo + deshabilitar mapa ---
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

// --- Inicialización principal ---
// Cargar query en setup antes de que el watcher de tags inicialice el multiselect
loadFromRoute()

onMounted(async () => {
  // Si la URL trae provincia → cargar ciudades
  if (provinceValue.value !== 'Provincia') {
    await fetchCities(provinceValue.value)
  }
})

// Cuando cambian los tags (props) desde el padre, reconstruir el multiselect
watch(
  () => props.tags,
  async (newTags) => {
    if (newTags && newTags.length > 0) {
      await nextTick()
      initMultiSelect()
    }
  },
  { immediate: true }
)

// Mantener formulario sincronizado si cambia la URL (ej: botón atrás del navegador)
watch(
  () => rout.query,
  async () => {
    loadFromRoute()
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
