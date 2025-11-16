<template>
  <section class="flex flex-col items-center justify-center text-center py-20 space-y-8 h-screen">
    <p class="opacity-40 absolute text-[450px]">🚧</p>
    <div class="max-w-2xl space-y-6 bg-gray-200/70 z-10 p-6 rounded-2xl mx-24 shadow-lg">
      <h2 class="text-4xl font-bold text-proyecto-primary">
        Portal en mantenimiento
      </h2>

      <p class="text-lg text-gray-700 leading-relaxed whitespace-pre-line">
        {{ message }}
      </p>

      <p class="text-sm text-gray-600">
        Estamos trabajando para volver lo antes posible.
        Esta página se actualizará automáticamente.
      </p>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { maintenanceState } from '@/utils/maintenanceState'
import { ensurePortalAvailability } from '@/router'

const router = useRouter()

const DEFAULT_MESSAGE = 'El portal se encuentra temporalmente en mantenimiento.'
const message = computed(() => maintenanceState.message?.trim() || DEFAULT_MESSAGE)

let intervalId = null

onMounted(() => {
  // Verificar cada 5 segundos si el portal ya no está en mantenimiento
  intervalId = setInterval(async () => {
    await ensurePortalAvailability(true)

    if (!maintenanceState.isActive) {
      // Salió del mantenimiento → redirigir al home
      router.push('/')
      console.log("Portal disponible nuevamente, redirigiendo al home.")
      // Opcional pero recomendado: refrescar completamente la vista
      window.location.reload()
    } else {
      console.log("Portal aún en mantenimiento.")
    }
  }, 5000)
})

onUnmounted(() => {
  clearInterval(intervalId)
})
</script>
