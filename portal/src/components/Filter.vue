<template>
  <form class="m-auto">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
      <!-- Provincia -->
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

      <!-- Nombre del sitio -->
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

      <!-- Favoritos (con tooltip cuando no está autenticado) -->
      <div
        class="p-2 border rounded-md text-sm bg-gray-50 focus:ring-blue-500
               focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600
               dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500
               dark:focus:border-blue-500 relative"
        :class="!authStore.isAuthenticated ? 'opacity-50 cursor-not-allowed group' : ''"
      >
        <input
          id="bordered-checkbox-1"
          v-model="favoriteValue"
          type="checkbox"
          :disabled="!authStore.isAuthenticated"
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

        <!-- Tooltip para usuario no autenticado -->
        <span
          v-if="!authStore.isAuthenticated"
          class="absolute left-0 top-full mt-1 text-xs bg-black text-white px-2 py-1
                 rounded hidden group-hover:block z-10"
        >
          Inicia sesión para usar favoritos
        </span>
      </div>

      <!-- Botón Filtrar -->
      <div
        class="col-start-2 row-start-3 md:col-start-4 md:row-start-1"
        :class="authStore.isAuthenticated ? 'flex flex-col gap-1' : 'flex gap-1'"
      >
        <router-link
          :to="{
            query: {
              province: provinceValue !== 'Provincia' ? provinceValue : undefined,
              city: cityValue !== 'Ciudad' ? cityValue : undefined,
              name: nameValue || undefined,
              description: descrpitionValue || undefined,
              tags: tagsValue.length ? tagsValue.join(',') : undefined,
              order_by: orderByValue !== 'Ordenar por' ? orderByValue : undefined,
              favorites: favoriteValue || undefined,
              page: props.page
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

      <!-- Ciudad -->
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

      <!-- Descripción -->
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

      <!-- Ordenar por -->
      <div>
        <select
          id="order"
          v-model="orderByValue"
          class="block w-full p-2 text-sm text-gray-900 border border-gray-300
                 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500
                 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400
                 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
        >
          <option selected>Ordenar por</option>
          <option value="oldest">Más antiguos primero</option>
          <option value="latest">Más recientes primero</option>
          <option value="rating-1-5">Reseñas 1-5 estrellas</option>
          <option value="rating-5-1">Reseñas 5-1 estrellas</option>
        </select>
      </div>

      <!-- Botón Restaurar -->
      <router-link
        @click="handleReset"
        :to="{ query: {} }"
        class="text-white w-full bg-proyecto-primary hover:bg-proyecto-accent
               focus:ring-2 focus:ring-offset-2 focus:ring-proyecto-accent transition
               font-medium rounded-lg text-sm px-5 py-2.5 text-center
               dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none
               dark:focus:ring-blue-800"
      >
        Limpiar filtros
      </router-link>
    </div>

    <!-- Tags multiselect -->
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
import { ref, watch, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/axios.js'

const authStore = useAuthStore()
const emit = defineEmits(['disableMap'])
const rout = useRoute()

const cityValue = ref('Ciudad')
const nameValue = ref('')
const provinceValue = ref('Provincia')
const descrpitionValue = ref('')
const orderByValue = ref('Ordenar por')
const favoriteValue = ref(false)
const tagsValue = ref([])

const cities = ref([])
const props = defineProps(['provinces', 'states', 'page', 'tags'])

// Variable para mantener referencia a la instancia del multiselect
let multiSelectInstance = null

function loadFromRoute(q = rout.query) {
  provinceValue.value = q.province || 'Provincia'
  cityValue.value = q.city || 'Ciudad'
  nameValue.value = q.name || ''
  descrpitionValue.value = q.description || ''
  orderByValue.value = q.orderBy || 'Ordenar por'
  favoriteValue.value = q.favorites === 'true'
  tagsValue.value = q.tags ? q.tags.split(',') : []
}

function destroyMultiSelect() {
  // Eliminar el contenedor creado por MultiSelectTag
  const container = document.querySelector('.multi-select-tag')
  if (container) {
    container.remove()
  }

  // Mostrar el select original nuevamente
  const tagsSelect = document.getElementById('tags')
  if (tagsSelect) {
    tagsSelect.style.display = ''
  }

  multiSelectInstance = null
}

function initMultiSelect() {
  // Destruir instancia previa si existe
  destroyMultiSelect()

  // Sincronizar atributos selected del <select> con tagsValue ANTES de crear MultiSelectTag
  const tagsSelect = document.getElementById('tags')
  if (tagsSelect) {
    Array.from(tagsSelect.options).forEach(opt => {
      opt.selected = tagsValue.value.includes(opt.value)
    })
  }

  multiSelectInstance = new MultiSelectTag('tags', {
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
  }
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

const handleReset = () => {
  provinceValue.value = 'Provincia'
  cityValue.value = 'Ciudad'
  nameValue.value = ''
  descrpitionValue.value = ''
  orderByValue.value = 'Ordenar por'
  favoriteValue.value = false
  tagsValue.value = []
  cities.value = []

  disableMapClick()

  nextTick(() => {
    initMultiSelect()
  })
}

const disableMapClick = () => {
  emit('disableMap')
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

/* Asegurar que el multiselect aparezca sobre el mapa */
.multi-select-tag {
  position: relative;
  z-index: 1000 !important;
}

/* El dropdown de opciones también debe tener z-index alto */
.multi-select-tag .wrapper {
  z-index: 1001 !important;
}
</style>
